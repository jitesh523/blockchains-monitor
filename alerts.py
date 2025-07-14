"""
alerts.py
Stub module for push-based alerting. In production, implement services for email, webhooks, and Slack/Discord alerts.
"""
import os
import requests
import smtplib
from typing import Dict, Any

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")

# Example usage: alert_user('Risk breached', 'Threshold exceeded', channel='slack')
def alert_user(title: str, message: str, channel: str = "email", metadata: Dict[str, Any] = None):
    if channel == "email":
        if not all([SMTP_SERVER, SMTP_USER, SMTP_PASS, EMAIL_TO]):
            print(f"[EMAIL ALERT FALLBACK]: {title} — {message} (missing SMTP config)")
        else:
            send_email_alert(title, message)
    elif channel == "slack":
        if not SLACK_WEBHOOK_URL:
            print(f"[SLACK ALERT FALLBACK]: {title} — {message} (missing SLACK_WEBHOOK_URL)")
        else:
            send_slack_alert(title, message, metadata)
    elif channel == "webhook":
        # Example generic webhook implementation can be added here
        print(f"[WEBHOOK ALERT]: {title} — {message}")
    else:
        print(f"[UNKNOWN ALERT CHANNEL]: {title} — {message}")

    if metadata:
        print(f"Metadata: {metadata}")

def send_slack_alert(title, message, metadata=None):
    payload = {"text": f"*{title}*: {message}"}
    if metadata:
        payload["attachments"] = [{"fields": [{"title": k, "value": str(v)} for k, v in metadata.items()]}]
    try:
        resp = requests.post(SLACK_WEBHOOK_URL, json=payload)
        resp.raise_for_status()
        print("[SLACK] Alert sent successfully.")
    except Exception as e:
        print(f"[SLACK] Sending failed: {e}")

def send_email_alert(subject, body):
    if not all([SMTP_SERVER, SMTP_USER, SMTP_PASS, EMAIL_TO]):
        print("Missing SMTP configuration.")
        return
    msg = f"Subject: {subject}\nTo: {EMAIL_TO}\nFrom: {SMTP_USER}\n\n{body}"
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, EMAIL_TO, msg)
        print("[EMAIL] Alert sent successfully.")
    except Exception as e:
        print(f"[EMAIL] Sending failed: {e}")

# Example trigger
if __name__ == "__main__":
    alert_user(
        title="Risk Breach Detected",
        message="Upgrade X introduces abnormal volatility.",
        channel="slack",
        metadata={"risk_score": 99, "chain": "Ethereum"}
    )

