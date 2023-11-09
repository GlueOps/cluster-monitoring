import os

class ServiceConfig:
    def __init__(self):
        if os.getenv('KUBERNETES_SERVICE_HOST'):
            print("Setting up for Kubernetes environment.")
            self._setup_kubernetes_config()
        else:
            print("Setting up for local environment.")
            self._setup_local_config()

        # New environment variable settings
        self.OPSGENIE_API_KEY = os.getenv('OPSGENIE_API_KEY')
        self.OPSGENIE_HEARTBEAT_NAME = os.getenv('OPSGENIE_HEARTBEAT_NAME')
        self.OPSGENIE_PING_INTERVAL_MINUTES = int(os.getenv('OPSGENIE_PING_INTERVAL_MINUTES', 3))


    def _setup_kubernetes_config(self):
        suffix = "glueops-core-kube-prometheus-stack.svc.cluster.local"
        self.prometheus = f"kps-prometheus.{suffix}:9090"
        self.alertmanager = f"kps-alertmanager.{suffix}:9093"
        self._set_urls()

    def _setup_local_config(self):
        self.prometheus = "localhost:9090"
        self.alertmanager = "localhost:9093"
        self._set_urls()

    def _set_urls(self):
        self.PROMETHEUS_URL_HEALTH = f"http://{self.prometheus}/-/healthy"
        self.ALERTMANAGER_URL_HEALTH = f"http://{self.alertmanager}/-/healthy"
        self.PROMETHEUS_URL_READY = f"http://{self.prometheus}/-/ready"
        self.ALERTMANAGER_URL_READY = f"http://{self.alertmanager}/-/ready"
        self.PROMETHEUS_QUERY_URL = f"http://{self.prometheus}/api/v1/query"
