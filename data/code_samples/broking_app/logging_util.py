"""SYNTHETIC demo file. Intentionally logs client PII."""
import logging

logger = logging.getLogger("broking")

API_KEY = "sk_live_abc123def456ghi789"  # hardcoded secret


def log_client_onboarding(client):
    logger.info("onboarded client pan=%s account_number=%s", client.pan, client.account_number)
