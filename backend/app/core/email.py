"""Best-effort transactional email over SMTP.

If SMTP isn't configured, sending is a logged no-op — features that send email
(team invites, etc.) still work via copyable links; they just skip delivery.
The actual send runs in a worker thread so it never blocks the event loop.
"""

from __future__ import annotations

import asyncio
import logging
import smtplib
import ssl
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger(__name__)


def email_configured() -> bool:
    return bool(
        settings.SMTP_HOST
        and settings.SMTP_USERNAME
        and settings.SMTP_PASSWORD
        and settings.SMTP_FROM
    )


def _send_sync(to: str, subject: str, text: str, html: str | None) -> None:
    msg = EmailMessage()
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(text)
    if html:
        msg.add_alternative(html, subtype="html")

    context = ssl.create_default_context()
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
        server.starttls(context=context)
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.send_message(msg)


async def send_email(to: str, subject: str, text: str, html: str | None = None) -> bool:
    """Send an email; returns True if delivered, False if skipped/failed."""
    if not email_configured():
        logger.info("SMTP not configured; skipping email to %s (%r)", to, subject)
        return False
    try:
        await asyncio.to_thread(_send_sync, to, subject, text, html)
        return True
    except Exception as exc:  # noqa: BLE001 - delivery is best-effort
        logger.warning("Failed to send email to %s: %s", to, exc)
        return False
