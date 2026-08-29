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

# Ceiling on how long to keep retrying a failed heartbeat ping. The effective
# budget is derived from `frequency` at startup (see __main__) so that a fully
# exhausted retry can never overrun its own tick.
HEARTBEAT_RETRY_BUDGET_SECONDS = 90

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
    return re.sub(r'(\?|&)(token=)[^&\s]*', r'\1\2***', url)


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
        logger.warning(f"  [FAIL] {label} — {type(e).__name__}: {mask_token(str(e))} ({url})")
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
        logger.warning(f"  [FAIL] alertmanager webhook notifications — {type(e).__name__}: {mask_token(str(e))}")
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


def send_incident_io_heartbeat(config: ServiceConfig, budget: float, backoff: int = 2) -> bool:
    """Ping incident.io's heartbeat URL, retrying transient failures in place.

    Auth is in the URL itself (`?token=...`), so a plain GET is enough, and GET is
    idempotent — safe to retry a read timeout. Retrying in place matters because the
    next cycle is a full tick away; losing a whole tick to one blip is what used to
    push us past incident.io's heartbeat deadline.

    4xx responses (bad or rotated token, wrong URL) are permanent and are NOT retried —
    retrying them would burn the entire budget every cycle, forever. Transient failures
    log at WARNING per attempt so a degrading link is visible before it fails outright.

    Returns True on success. Never raises: the daemon stays up and a real ping outage is
    surfaced by incident.io's own heartbeat-late alert, which is the right place for it."""
    masked = mask_token(config.INCIDENT_IO_HEARTBEAT_URL)
    started = time.monotonic()
    deadline = started + budget
    attempt = 0

    while True:
        attempt += 1
        try:
            response = session.get(config.INCIDENT_IO_HEARTBEAT_URL, timeout=HTTP_TIMEOUT)
            response.raise_for_status()
            logger.info(f"Heartbeat acknowledged (HTTP {response.status_code}, attempt {attempt})")
            return True
        except requests.HTTPError as e:
            status = e.response.status_code if e.response is not None else None
            # 408 (timeout) and 429 (rate limited) are worth another go; the rest of 4xx
            # is a config problem that no amount of retrying will fix.
            if status is not None and 400 <= status < 500 and status not in (408, 429):
                logger.error(f"Heartbeat rejected (HTTP {status}) — not retrying (url: {masked})")
                return False
            failure = f"HTTP {status}"
        except requests.RequestException as e:
            # mask_token the exception text too — HTTPError and ConnectionError messages
            # embed the full URL, query string and all.
            failure = f"{type(e).__name__}: {mask_token(str(e))}"

        remaining = deadline - time.monotonic()
        if remaining <= 0:
            elapsed = time.monotonic() - started
            logger.error(
                f"Heartbeat ping failed after {attempt} attempts / {elapsed:.0f}s — "
                f"{failure} (url: {masked})"
            )
            return False

        sleep_for = min(backoff, remaining)
        logger.warning(
            f"Heartbeat attempt {attempt} failed — {failure}; "
            f"retrying in {sleep_for:.0f}s ({remaining:.0f}s budget left)"
        )
        time.sleep(sleep_for)
        backoff = min(backoff * 2, 10)


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

    # Every tick runs the checks and pings, so this — not the interval — is the ping
    # cadence. The interval only scales it, and sets the back-off when unhealthy.
    frequency = max(interval_in_seconds / 2, 60)

    # Keep a fully exhausted retry (budget + one final HTTP_TIMEOUT) inside one tick, so
    # a failed ping can never push the next cycle late.
    retry_budget = min(HEARTBEAT_RETRY_BUDGET_SECONDS, max(0, frequency - HTTP_TIMEOUT - 10))

    # Boot-time visibility — what we're configured with, who we're pinging.
    logger.info("Starting GlueOps cluster monitoring")
    logger.info(
        f"Config: ping_cadence={int(frequency)}s, heartbeat_retry_budget={int(retry_budget)}s, "
        f"unhealthy_backoff={interval_in_seconds}s"
    )
    logger.info(f"Heartbeat URL: {mask_token(config.INCIDENT_IO_HEARTBEAT_URL)}")
    logger.info(f"Prometheus:    {config.prometheus}")
    logger.info(f"Alertmanager:  {config.alertmanager}")

    while True:
        cycle_start = time.monotonic()

        logger.info("Running cluster health checks")
        all_passed, failed_count, total_count = run_all_health_checks(config)

        if all_passed:
            logger.info(f"All {total_count} checks passed — pinging incident.io heartbeat")
            send_incident_io_heartbeat(config, retry_budget)
        else:
            logger.error(f"{failed_count} of {total_count} checks failed — skipping heartbeat ping")
            logger.info(f"Sleeping {interval_in_seconds}s before next attempt")
            time.sleep(interval_in_seconds)

        # Fixed-rate tick: retry time is absorbed by the interval rather than added to
        # it, so an exhausted retry budget doesn't push the next ping late. Measured
        # from cycle_start (not a fixed epoch) so an overrunning cycle slips the
        # schedule instead of firing a catch-up burst.
        time.sleep(max(0.0, frequency - (time.monotonic() - cycle_start)))
