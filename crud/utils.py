import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def send_to_zapier(payload):
    """
    Send a JSON payload to the Zapier webhook URL.
    """
    webhook_url = getattr(settings, 'ZAPIER_WEBHOOK_URL', None)
    if not webhook_url:
        logger.error("Zapier webhook URL is not configured in settings.")
        return False
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info(f"Successfully sent data to Zapier: {payload}")
        return True
    except requests.RequestException as e:
        logger.error(f"Failed to send data to Zapier: {e}")
        return False
