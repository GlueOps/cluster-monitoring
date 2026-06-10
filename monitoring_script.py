import os
import re
import time

import requests
from glueops.setup_logging import configure as go_configure_logging

from serviceconfig import ServiceConfig

logger = go_configure_logging(
    name='GLUEOPS_CLUSTER_MONITORING',
    level=os.getenv('PYTHON_LOG_LEVEL', 'INFO')
)

# Network call timeout (seconds). Prevents the daemon from hanging if a
# downstream service stops responding cleanly.
HTTP_TIMEOUT = 10

# Shared session: keep-alive + connection pooling across the 6 calls per cycle,
# and a single User-Agent string so downstream logs (Prometheus/Alertmanager/
# incident.io) attribute requests to this app.
session = requests.Session()
session.headers.update({"User-Agent": "glueops-cluster-monitoring"})


def mask_token(url: str | None) -> str | None:
    """Replace the `?token=...` (or `&token=...`) query value with `***` so the
    credential never appears in logs."""
    if not url:
        return url
    return re.sub(r'(\?|&)(token=)[^&]*', r'\1\2***', url)


def check_url_responds_200(url: str, label: str) -> bool:
    """Probe a URL with GET; return True on HTTP 200. Logs result with context.
    Catches transient network errors and returns False — never raises."""
    try:
        response = session.get(url, timeout=HTTP_TIMEOUT)
        if response.status_code == 200:
            logger.info(f"  [OK]   {label}")
            return True
        logger.warning(f"  [FAIL] {label} — HTTP {response.status_code} from {url}")
        return False
    except requests.RequestException as e:
        logger.warning(f"  [FAIL] {label} — {type(e).__name__}: {e} ({url})")
        return False


def check_alertmanager_webhook_notifications(prometheus_query_url: str) -> bool:
    """Returns True only if there have been zero failed Alertmanager webhook
    notifications in the last 10 minutes. Catches the case where the link from
    the cluster to incident.io (or any other webhook receiver) is broken.

    Filter is `integration="webhook"` — covers all webhook receivers collectively;
    the `receiver` label isn't populated on this metric here.

    Catches transient network errors. Malformed Prometheus responses (unexpected
    JSON shape) are intentionally NOT caught — they propagate and crash the
    daemon so Kubernetes restarts it and the issue gets surfaced loudly."""
    query = 'sum(increase(alertmanager_notifications_failed_total{integration="webhook"}[10m]))'
    label = "alertmanager webhook notifications (last 10m: 0 failures)"

    try:
        response = session.get(prometheus_query_url, params={'query': query}, timeout=HTTP_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.warning(f"  [FAIL] alertmanager webhook notifications — {type(e).__name__}: {e}")
        return False

    result = response.json()

    if result.get('status') != 'success':
        logger.warning(f"  [FAIL] alertmanager webhook notifications — Prometheus returned status={result.get('status')}")
        return False

    data = result.get('data', {})
    if data.get('resultType') != 'vector' or not data.get('result'):
        # No samples in the window = no failures recorded = healthy
        logger.info(f"  [OK]   alertmanager webhook notifications (no failure samples in window)")
        return True

    value = float(data['result'][0]['value'][1])
    if value == 0:
        logger.info(f"  [OK]   {label}")
        return True
    logger.warning(f"  [FAIL] alertmanager webhook notifications — last 10m: {value:.0f} failures")
    return False


def run_all_health_checks(config: ServiceConfig) -> tuple[bool, int, int]:
    """Run all 5 health checks unconditionally and return (all_passed, failed_count, total_count).
    Uses an explicit list (not short-circuit `and`) so every check runs and logs even when
    earlier ones fail — gives a complete picture per cycle."""
    results = [
        check_alertmanager_webhook_notifications(config.PROMETHEUS_QUERY_URL),
        check_url_responds_200(config.PROMETHEUS_URL_HEALTH,    "prometheus /-/healthy"),
        check_url_responds_200(config.PROMETHEUS_URL_READY,     "prometheus /-/ready"),
        check_url_responds_200(config.ALERTMANAGER_URL_HEALTH,  "alertmanager /-/healthy"),
        check_url_responds_200(config.ALERTMANAGER_URL_READY,   "alertmanager /-/ready"),
    ]
    failed = sum(1 for r in results if not r)
    return failed == 0, failed, len(results)


def send_incident_io_heartbeat(config: ServiceConfig) -> bool:
    """Ping incident.io's heartbeat URL. Auth is in the URL itself (`?token=...`),
    so a plain GET is enough.

    Logs + returns False on transient failure rather than raising — the daemon stays
    up and a real ping outage will be surfaced by incident.io's own heartbeat-late
    alert (which is the right place for that signal)."""
    masked = mask_token(config.INCIDENT_IO_HEARTBEAT_URL)
    try:
        response = session.get(config.INCIDENT_IO_HEARTBEAT_URL, timeout=HTTP_TIMEOUT)
        response.raise_for_status()
        logger.info(f"Heartbeat acknowledged (HTTP {response.status_code})")
        return True
    except requests.RequestException as e:
        logger.error(f"Heartbeat ping failed — {type(e).__name__}: {e} (url: {masked})")
        return False


if __name__ == '__main__':
    config = ServiceConfig()

    # Config validation — unrecoverable misconfigurations, so exit.
    if not config.INCIDENT_IO_HEARTBEAT_URL:
        logger.critical("INCIDENT_IO_HEARTBEAT_URL is not set — refusing to start.")
        raise SystemExit(1)

    interval_in_seconds = config.INCIDENT_IO_PING_INTERVAL_MINUTES * 60
    if interval_in_seconds < 60:
        logger.critical("INCIDENT_IO_PING_INTERVAL_MINUTES must be >= 1 — refusing to start.")
        raise SystemExit(1)

    # The frequency is half the interval but not less than 1 minute.
    frequency = max(interval_in_seconds / 2, 60)

    # Boot-time visibility — what we're configured with, who we're pinging.
    logger.info("Starting GlueOps cluster monitoring")
    logger.info(f"Config: ping_interval={config.INCIDENT_IO_PING_INTERVAL_MINUTES} min, check_frequency={int(frequency)}s")
    logger.info(f"Heartbeat URL: {mask_token(config.INCIDENT_IO_HEARTBEAT_URL)}")
    logger.info(f"Prometheus:    {config.prometheus}")
    logger.info(f"Alertmanager:  {config.alertmanager}")

    execution_count = 0

    while True:
        if execution_count < 2:
            logger.info("Running cluster health checks")
            all_passed, failed_count, total_count = run_all_health_checks(config)

            if all_passed:
                logger.info(f"All {total_count} checks passed — pinging incident.io heartbeat")
                send_incident_io_heartbeat(config)
            else:
                logger.error(f"{failed_count} of {total_count} checks failed — skipping heartbeat ping")
                logger.info(f"Sleeping {interval_in_seconds}s before next attempt")
                time.sleep(interval_in_seconds)

            execution_count += 1
        else:
            # Reset the count and sleep for the full interval before checking again.
            execution_count = 0

        time.sleep(frequency)
