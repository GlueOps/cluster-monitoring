# GLUEOPS CLUSTER MONITORING

This application is designed for monitoring a Kubernetes cluster with the Prometheus and Alertmanager components from the Kubernetes Prometheus Stack (KPS).

## Configuration

Before running the application, make sure to configure the following environment variables:

- `OPSGENIE_API_KEY`: Your Opsgenie API key for sending heartbeat notifications.
- `OPSGENIE_HEARTBEAT_NAME`: The name of the Opsgenie heartbeat to ping.
- `OPSGENIE_PING_INTERVAL_MINUTES`: The interval (in minutes) between pinging the Opsgenie heartbeat (default: 2 minutes).

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
