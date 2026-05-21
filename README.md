# GLUEOPS CLUSTER MONITORING

This application is designed for monitoring a Kubernetes cluster with the Prometheus and Alertmanager components from the Kubernetes Prometheus Stack (KPS).

It pings an incident.io heartbeat URL on a regular interval *only when* the cluster's Prometheus + Alertmanager are healthy and there have been no failed Alertmanager webhook notifications in the last 10 minutes. If any of those checks fail, the heartbeat is not sent, which causes the cluster's incident.io heartbeat alert to fire.

## Configuration

Before running the application, make sure to configure the following environment variables:

- `INCIDENT_IO_HEARTBEAT_URL`: Full authenticated URL for the cluster's incident.io heartbeat source. Includes the `?token=...` query parameter; no Authorization header is needed. Copy it from the incident.io web UI under **Alerts → Alert sources → Heartbeat · `<captain_domain>`**.
- `INCIDENT_IO_PING_INTERVAL_MINUTES`: The interval (in minutes) between pinging the incident.io heartbeat (default: 3 minutes; minimum: 1 minute).
- `PYTHON_LOG_LEVEL`: Optional log level. Defaults to `INFO`.

## Running in a Kubernetes Cluster

To run this application within a Kubernetes cluster, follow these steps:

1. Ensure your Kubernetes cluster is up and running.
2. Deploy the application with the configured environment variables.
3. The application will automatically detect its environment and use in-cluster URLs for Prometheus and Alertmanager.

## Running Locally for Debugging

To run this application locally for debugging purposes and access Prometheus and Alertmanager, you can set up port forwarding to your cluster. Follow these steps:

1. Ensure you have `kubectl` installed and configured to communicate with your Kubernetes cluster.
2. Identify the Prometheus and Alertmanager pods in your cluster:

   ```bash
   # For Prometheus
   kubectl port-forward svc/kps-prometheus 9090:9090 -n glueops-core-kube-prometheus-stack
   # For Alertmanager
   kubectl port-forward svc/kps-alertmanager 9093:9093 -n glueops-core-kube-prometheus-stack
   ```
