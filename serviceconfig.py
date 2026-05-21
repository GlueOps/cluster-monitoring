import logging
import os

# Same logger name as monitoring_script — by the time ServiceConfig() runs,
# go_configure_logging has already configured this logger with the JSON
# formatter, so messages flow through the same pipeline.
logger = logging.getLogger("GLUEOPS_CLUSTER_MONITORING")


class ServiceConfig:
    def __init__(self) -> None:
        if os.getenv('KUBERNETES_SERVICE_HOST'):
            logger.info("Setting up for Kubernetes environment")
            self._setup_kubernetes_config()
        else:
            logger.info("Setting up for local environment")
            self._setup_local_config()

        # incident.io heartbeat settings
        self.INCIDENT_IO_HEARTBEAT_URL: str | None = os.getenv('INCIDENT_IO_HEARTBEAT_URL')
        self.INCIDENT_IO_PING_INTERVAL_MINUTES: int = int(os.getenv('INCIDENT_IO_PING_INTERVAL_MINUTES', '3'))

    def _setup_kubernetes_config(self) -> None:
        suffix = "glueops-core-kube-prometheus-stack.svc.cluster.local"
        self.prometheus = f"kps-prometheus.{suffix}:9090"
        self.alertmanager = f"kps-alertmanager.{suffix}:9093"
        self._set_urls()

    def _setup_local_config(self) -> None:
        self.prometheus = "localhost:9090"
        self.alertmanager = "localhost:9093"
        self._set_urls()

    def _set_urls(self) -> None:
        self.PROMETHEUS_URL_HEALTH = f"http://{self.prometheus}/-/healthy"
        self.ALERTMANAGER_URL_HEALTH = f"http://{self.alertmanager}/-/healthy"
        self.PROMETHEUS_URL_READY = f"http://{self.prometheus}/-/ready"
        self.ALERTMANAGER_URL_READY = f"http://{self.alertmanager}/-/ready"
        self.PROMETHEUS_QUERY_URL = f"http://{self.prometheus}/api/v1/query"
