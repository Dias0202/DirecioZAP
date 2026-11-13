"""Validation of the ``X-Twilio-Signature`` header on inbound webhooks.

Twilio signs every webhook request with HMAC-SHA1, keyed by the account auth
token, over the full public URL of the request followed by each POST parameter
name and value, sorted by name. See
https://www.twilio.com/docs/usage/security#validating-requests

Implemented with the standard library so the bot does not depend on the Twilio
SDK only for this check.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
from typing import Iterable, Tuple


def compute_signature(url: str, params: Iterable[Tuple[str, str]], auth_token: str) -> str:
    """Return the base64 HMAC-SHA1 signature Twilio sends for ``url`` and ``params``."""
    payload = url + "".join(f"{key}{value}" for key, value in sorted(params))
    digest = hmac.new(auth_token.encode("utf-8"), payload.encode("utf-8"), hashlib.sha1).digest()
    return base64.b64encode(digest).decode("ascii")


def is_valid_signature(
    url: str,
    params: Iterable[Tuple[str, str]],
    signature: str | None,
    auth_token: str,
) -> bool:
    """Check a received signature in constant time. A missing signature is invalid."""
    if not signature or not auth_token:
        return False
    expected = compute_signature(url, params, auth_token)
    return hmac.compare_digest(expected, signature)
