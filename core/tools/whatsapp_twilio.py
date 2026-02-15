"""
Minimal Twilio WhatsApp send.
Uses Django settings: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN,
TWILIO_WHATSAPP_NUMBER (from), TWILIO_WHATSAPP_TO (recipient).
"""
from __future__ import annotations

import logging
from typing import List

from django.conf import settings

logger = logging.getLogger(__name__)

try:
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException
    _TWILIO_AVAILABLE = True
except ImportError:
    Client = None
    TwilioRestException = None
    _TWILIO_AVAILABLE = False


def get_twilio_client():
    """Create Twilio client using settings."""
    sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
    token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
    if not sid or not token:
        raise ValueError("TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN must be set in settings/.env")
    return Client(sid, token)


def send_whatsapp_message(to: str, text: str) -> str:
    """
    Send a single WhatsApp message via Twilio.

    Args:
        to: Recipient phone number (e.g. +962777381408)
        text: Message body text

    Returns:
        Twilio message SID on success.
    """
    if not _TWILIO_AVAILABLE:
        raise RuntimeError("twilio not installed. Run: pip install twilio")

    client = get_twilio_client()
    from_ = getattr(settings, 'TWILIO_WHATSAPP_NUMBER', '')
    if not from_:
        raise ValueError("TWILIO_WHATSAPP_NUMBER must be set in settings/.env")

    # Add whatsapp: prefix if missing
    if not from_.startswith("whatsapp:"):
        from_ = f"whatsapp:{from_}"
    if not to.startswith("whatsapp:"):
        to = f"whatsapp:{to}"

    try:
        resp = client.messages.create(
            body=text,
            from_=from_,
            to=to,
        )
        logger.info(f"WhatsApp message sent: SID={resp.sid}")
        return resp.sid
    except Exception as e:
        if hasattr(e, 'code') and e.code == 63007:
            raise RuntimeError(
                "Twilio error 63007: Invalid WhatsApp 'From' number. "
                "Use the WhatsApp Sandbox number (e.g. +14155238886) from "
                "Twilio Console -> Messaging -> Try it out -> Send a WhatsApp message."
            ) from e
        raise
