import requests
import time
import logging
from json_log_formatter import JsonFormatter
import json
import os
from dotenv import load_dotenv

load_dotenv()

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
        'PING_SLEEP_SECONDS': int(os.getenv('PING_SLEEP_SECONDS'))
    }
    missing_vars = [var for var, value in env_vars.items() if not value]

    if missing_vars:
        for var in missing_vars:
            logger.error(f'Environment variable {var} is not set.')
        exit(1)

    return env_vars

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
     
    logger = setup_logger()
    env_vars = get_env_vars()
    OPSGENIE_API_KEY = env_vars['OPSGENIE_API_KEY']
    CLUSTER_NAME = env_vars['CLUSTER_NAME']
    PING_SLEEP_SECONDS= env_vars['PING_SLEEP_SECONDS']

    try:
        while True:
            ping_opsgenie_heartbeat()
            time.sleep(PING_SLEEP_SECONDS) 
    except KeyboardInterrupt:
            logger.info("Opsgenie pinger stopped by keyboard.")

if __name__ == "__main__":
    main()
