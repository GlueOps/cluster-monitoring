import requests
import time
import logging
from dotenv import load_dotenv
from json_log_formatter import JsonFormatter
import json
import os

def setup_logger():
    logger = logging.getLogger('OpsgeniePing')

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = JsonFormatter()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(logging.INFO)
    return logger

def get_env_vars():
    env_vars = {
        'OPSGENIE_API_KEY': os.getenv('OPSGENIE_API_KEY'),
        'CLUSTER_NAME': os.getenv('CLUSTER_NAME'),
        'PING_SLEEP': int(os.getenv('PING_SLEEP'))
    }
    missing_vars = [var for var, value in env_vars.items() if not value]

    if missing_vars:
        for var in missing_vars:
            logger.error(f'Environment variable {var} is not set.')
        exit(1)

    return env_vars

def does_heartbeat_exist(CLUSTER_NAME, OPSGENIE_API_KEY):
    name = CLUSTER_NAME
    OPSGENIE_LIST_HEARTBEATS_URL = "https://api.opsgenie.com/v2/heartbeats"
    headers = {
        "Authorization": f"GenieKey {OPSGENIE_API_KEY}"
    }

    try:
        response = requests.get(OPSGENIE_LIST_HEARTBEATS_URL, headers=headers)
        response.raise_for_status()
        heartbeats_data = response.json().get('data', {}).get('heartbeats', [])
        for heartbeat in heartbeats_data:
            if heartbeat.get('name') == CLUSTER_NAME:
                return True
        return False
    except requests.RequestException as e:
        logger.error(f"Failed to retrieve list of heartbeats from Opsgenie. Error: {e}")
        return False

def ping_opsgenie_heartbeat():
    OPSGENIE_HEARTBEAT_URL = f"https://api.opsgenie.com/v2/heartbeats/{CLUSTER_NAME}/ping"
    headers = {
        "Authorization": f"GenieKey {OPSGENIE_API_KEY}"
    }

    try:
        response = requests.get(OPSGENIE_HEARTBEAT_URL, headers=headers)
        response.raise_for_status()
        logger.info("Pinged Opsgenie heartbeat successfully!")

    except requests.RequestException as e:
        logger.error(f"Failed to ping Opsgenie heartbeat. Error: {e}")

def main():
    global logger, OPSGENIE_API_KEY, CLUSTER_NAME
    
    load_dotenv()  # Load environment variables from .env file
    logger = setup_logger()
    env_vars = get_env_vars()
    OPSGENIE_API_KEY = env_vars['OPSGENIE_API_KEY']
    CLUSTER_NAME = env_vars['CLUSTER_NAME']
    PING_SLEEP= env_vars['PING_SLEEP']

    if not does_heartbeat_exist(CLUSTER_NAME, OPSGENIE_API_KEY):
        logger.error(f"Heartbeat {CLUSTER_NAME} does not exist in Opsgenie.")
    else:
        logger.info(f"Heartbeat {CLUSTER_NAME} exist in Opsgenie.")

        try:
            while True:
                ping_opsgenie_heartbeat()
                time.sleep(PING_SLEEP)  # Sleep for 5 minutes #make an env 
        except KeyboardInterrupt:
            logger.info("Opsgenie pinger stopped by keyboard.")

if __name__ == "__main__":
    main()