import os

import aiosmtplib
from email.message import EmailMessage

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
EMAIL_FROM = os.getenv("EMAIL_FROM", SMTP_USERNAME)


async def send_alert_email(to_email: str, bag_name: str) -> None:
    if not SMTP_HOST or not EMAIL_FROM:
        raise RuntimeError("SMTP configuration is incomplete. Set SMTP_HOST and EMAIL_FROM.")

    message = EmailMessage()
    message["From"] = EMAIL_FROM
    message["To"] = to_email
    message["Subject"] = f"Hermès bag available: {bag_name}"
    message.set_content(
        f"Good news! {bag_name} appears to be available for purchase now.\n"
        f"Check here: https://www.hermes.com/us/en/category/leather-goods/bags-and-clutches/womens-bags-and-clutches/#|"
    )

    await aiosmtplib.send(
        message,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        username=SMTP_USERNAME or None,
        password=SMTP_PASSWORD or None,
        start_tls=SMTP_USE_TLS,
    )
