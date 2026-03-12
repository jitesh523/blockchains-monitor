"""
alerts.py
Push-based alerting module with email, Slack, webhook, and fallback channels.
"""
import logging
import os
import smtplib
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")


def alert_user(
    title: str,
    message: str,
    channel: str = "email",
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """Dispatch an alert to the specified channel."""
    if channel == "email":
        if not all([SMTP_SERVER, SMTP_USER, SMTP_PASS, EMAIL_TO]):
            logger.warning("[EMAIL FALLBACK] %s — %s (missing SMTP config)", title, message)
        else:
            send_email_alert(title, message)
    elif channel == "slack":
        if not SLACK_WEBHOOK_URL:
            logger.warning("[SLACK FALLBACK] %s — %s (missing SLACK_WEBHOOK_URL)", title, message)
        else:
            send_slack_alert(title, message, metadata)
    elif channel == "webhook":
        logger.info("[WEBHOOK] %s — %s", title, message)
    else:
        logger.warning("[UNKNOWN CHANNEL=%s] %s — %s", channel, title, message)

    if metadata:
        logger.debug("Alert metadata: %s", metadata)


def send_slack_alert(
    title: str,
    message: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """Send an alert via Slack webhook."""
    payload: Dict[str, Any] = {"text": f"*{title}*: {message}"}
    if metadata:
        payload["attachments"] = [
            {"fields": [{"title": k, "value": str(v)} for k, v in metadata.items()]}
        ]
    try:
        resp = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
        resp.raise_for_status()
        logger.info("[SLACK] Alert sent: %s", title)
    except Exception as e:
        logger.error("[SLACK] Sending failed: %s", e)


def send_email_alert(subject: str, body: str) -> None:
    """Send an alert via SMTP email."""
    if not all([SMTP_SERVER, SMTP_USER, SMTP_PASS, EMAIL_TO]):
        logger.error("Missing SMTP configuration — cannot send email")
        return
    msg = f"Subject: {subject}\nTo: {EMAIL_TO}\nFrom: {SMTP_USER}\n\n{body}"
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, EMAIL_TO, msg)
        logger.info("[EMAIL] Alert sent: %s", subject)
    except Exception as e:
        logger.error("[EMAIL] Sending failed: %s", e)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    alert_user(
        title="Risk Breach Detected",
        message="Upgrade X introduces abnormal volatility.",
        channel="slack",
        metadata={"risk_score": 99, "chain": "Ethereum"},
    )
