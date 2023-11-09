import os
import requests
from glueops.setup_logging import configure as go_configure_logging

#=== configure logging
logger = go_configure_logging(
    name='GLUEOPS_CLUSTER_MONITORING',
    level=os.getenv('PYTHON_LOG_LEVEL', 'INFO')
)

OPSGENIE_API_KEY = os.getenv('OPSGENIE_API_KEY')
OPSGENIE_HEARTBEAT_NAME = os.getenv('OPSGENIE_HEARTBEAT_NAME')

CLUSTER_DEFAULT_DOMAIN_NAME = os.getenv(
    'CLUSTER_DEFAULT_DOMAIN_NAME',
    'cluster.local'
)
KUBE_PROMETHEUS_STACK_NAMESPACE = os.getenv(
    'KUBE_PROMETHEUS_STACK_NAMESPACE',
    'glueops-core-kube-prometheus-stack'
)

GLUEOPS_CORE_NAMESPACE = os.getenv(
    'GLUEOPS_CORE_NAMESPACE',
    'glueops-core'
)

PROMETHEUS_URL_HEALTH = f"kps-prometheus.{KUBE_PROMETHEUS_STACK_NAMESPACE}.svc.{CLUSTER_DEFAULT_DOMAIN_NAME}:9090/-/healthy"
PROMETHEUS_URL_READY = f"kps-prometheus.{KUBE_PROMETHEUS_STACK_NAMESPACE}.svc.{CLUSTER_DEFAULT_DOMAIN_NAME}:9090/-/ready"
ALERTMANAGER_URL_HEALTH = f"kps-alertmanager.{KUBE_PROMETHEUS_STACK_NAMESPACE}.svc.{CLUSTER_DEFAULT_DOMAIN_NAME}:9093/-/healthy"
ALERTMANAGER_URL_READY = f"kps-alertmanager.{KUBE_PROMETHEUS_STACK_NAMESPACE}.svc.{CLUSTER_DEFAULT_DOMAIN_NAME}:9093/-/ready"                

def is_cluster_healthy():
    return (
        get_alertmanager_notifification_health_for_opsgenie() and
        check_for_200_response(PROMETHEUS_URL_HEALTH) and
        check_for_200_response(PROMETHEUS_URL_READY) and
        check_for_200_response(ALERTMANAGER_URL_HEALTH) and
        check_for_200_response(ALERTMANAGER_URL_READY)
    )

def check_for_200_response(url):
    try:
        response = requests.get(url)
        # Check if the response code is 200
        if response.status_code == 200:
            return True
        else:
            logger.warning(f"BAD RESPONSE CODE: {response.status_code} FOR: {url}")
            return False
    except Exception as e:
        # In case of any exception (like network issue, invalid URL, etc.)
        logger.exception(f"An error occurred: {e}")
        raise


def get_alertmanager_notifification_health_for_opsgenie():
    # Prometheus query
    query = 'sum(increase(alertmanager_notifications_failed_total{integration="opsgenie"}[10m]))'
    # URL for the Prometheus HTTP API
    url = 'http://'+ KUBE_PROMETHEUS_STACK_NAMESPACE + ':9090/api/v1/query'

    # Parameters for the request
    params = {
        'query': query
    }

    try:
        # Send the request to Prometheus
        response = requests.get(url, params=params)
        response.raise_for_status()

        # Parse the JSON response
        result = response.json()

        # Check the status of the response
        if result['status'] == 'success':
            # Extract the result
            data = result.get('data', {})
            result_type = data.get('resultType', '')

            # Check if there are any results
            if result_type == 'vector' and data.get('result', []):
                # Get the value of the result
                value = float(data['result'][0]['value'][1])

                # Return True if the value is 0, False otherwise
                return value == 0

        return False

    except requests.RequestException as e:
        logger.exception(f"Error querying Prometheus: {e}")
        raise
    
def send_opsgenie_heartbeat(heartbeat_name):
    heart_eat_url = f"https://api.opsgenie.com/v2/heartbeats/{heartbeat_name}/ping"
    headers = {
        "Authorization": f"GenieKey {OPSGENIE_API_KEY}"
    }

    try:
        response = requests.get(heart_eat_url, headers=headers)
        response.raise_for_status()
        logger.info("Pinged Opsgenie heartbeat successfully!")

    except requests.RequestException as e:
        logger.exception(f"Failed to ping Opsgenie heartbeat. Error: {e}")
        raise

if __name__ == '__main__':
    while True:
        if is_cluster_healthy():
            logger.info("Checks: STARTED")
            send_opsgenie_heartbeat(OPSGENIE_HEARTBEAT_NAME)
            logger.info("Checks: PASSED")
        else:
            logger.error(f"One or more health checks failed. Heartbeat for {OPSGENIE_HEARTBEAT_NAME} was not sent")    
