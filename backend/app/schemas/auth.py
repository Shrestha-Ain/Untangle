"""
Pydantic schemas for authentication payloads.
"""

from pydantic import BaseModel


class ClerkJWTPayload(BaseModel):
    """Validated claims from a decoded Clerk session JWT."""

    sub: str  # Clerk user_id, e.g. "user_2abc..."
    exp: int  # Expiration timestamp
    iat: int  # Issued-at timestamp
    iss: str | None = None  # Issuer URL
    azp: str | None = None  # Authorized party (frontend origin)
    sid: str | None = None  # Session ID


class ClerkWebhookEvent(BaseModel):
    """
    Shape of a Clerk webhook event payload.

    Clerk sends these to our webhook endpoint for user lifecycle events:
    - user.created
    - user.updated
    - user.deleted
    """

    type: str
    data: dict
    object: str | None = None
