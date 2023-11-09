import os
import requests
from glueops.setup_logging import configure as go_configure_logging
import time
from serviceconfig import ServiceConfig

#=== configure logging
logger = go_configure_logging(
    name='GLUEOPS_CLUSTER_MONITORING',
    level=os.getenv('PYTHON_LOG_LEVEL', 'INFO')
)
      

def is_cluster_healthy(config):
    return (
        get_alertmanager_notifification_health_for_opsgenie(config.PROMETHEUS_QUERY_URL) and
        check_for_200_response(config.PROMETHEUS_URL_HEALTH) and
        check_for_200_response(config.PROMETHEUS_URL_READY) and
        check_for_200_response(config.ALERTMANAGER_URL_HEALTH) and
        check_for_200_response(config.ALERTMANAGER_URL_READY)
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


def get_alertmanager_notifification_health_for_opsgenie(prometheus_query_url):
    # Prometheus query
    query = 'sum(increase(alertmanager_notifications_failed_total{integration="opsgenie"}[10m]))'

    # Parameters for the request
    params = {
        'query': query
    }

    try:
        # Send the request to Prometheus
        response = requests.get(prometheus_query_url, params=params)
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
    
def send_opsgenie_heartbeat(config):
    url = f"https://api.opsgenie.com/v2/heartbeats/{config.OPSGENIE_HEARTBEAT_NAME}/ping"
    headers = {
        "Authorization": f"GenieKey {config.OPSGENIE_API_KEY}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        logger.debug("Pinged Opsgenie heartbeat successfully!")

    except requests.RequestException as e:
        logger.exception(f"Failed to send Opsgenie heartbeat. Error: {e}")
        raise
    
if __name__ == '__main__':
    config = ServiceConfig()   
    interval_in_seconds = config.OPSGENIE_PING_INTERVAL_MINUTES * 60

    # Check if the interval is less than 1 minute
    if interval_in_seconds < 60:
        try:
            raise ValueError("OPSGENIE_PING_INTERVAL_MINUTES must be 1 minute or greater.")
        except Exception as e:
            logger.exception(str(e))
            raise
    

    # The frequency is half the interval but not less than 1 minute
    frequency = max(interval_in_seconds / 2, 60)
    execution_count = 0

    while True:
        if execution_count < 2:
            if is_cluster_healthy(config):
                logger.info("Checks: STARTED")
                #send_opsgenie_heartbeat(config.OPSGENIE_HEARTBEAT_NAME)
                logger.info("Checks: PASSED")
            else:
                logger.error(f"One or more health checks failed. Heartbeat for {config.OPSGENIE_HEARTBEAT_NAME} was not sent")   
                logger.info(f"Waiting {interval_in_seconds+120} seconds before checking again")
                time.sleep(interval_in_seconds+120) 
            execution_count += 1
        else:
            # Reset the count and sleep for the full interval before checking again
            execution_count = 0
            time.sleep(interval_in_seconds - 2 * frequency)
        time.sleep(frequency)
        
