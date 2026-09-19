"""
Authentication endpoints.

- GET  /auth/me      — return the currently authenticated user's profile
- POST /auth/webhook — receive Clerk lifecycle events (user.created/updated/deleted)
"""

import json
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.security import verify_webhook_signature
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserRead
from app.services import user_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/me", response_model=UserRead)
def get_me(user: Annotated[User, Depends(get_current_active_user)]):
    """
    Return the currently authenticated user's profile.

    This is the endpoint the frontend calls after Clerk login to confirm
    backend connectivity and sync user data. It also triggers JIT
    provisioning if this is the user's first request.
    """
    return user


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def clerk_webhook(request: Request, db: Annotated[Session, Depends(get_db)]):
    """
    Receive Clerk webhook events for user lifecycle management.

    Expected events:
    - user.created  → create local user record
    - user.updated  → update email/name/image
    - user.deleted  → soft-delete (deactivate)

    The webhook payload is verified using the svix signature
    before processing. Clerk must be configured to send events
    to this endpoint with the matching CLERK_WEBHOOK_SECRET.
    """
    # Read raw body for signature verification
    body = await request.body()
    headers = dict(request.headers)

    # Verify svix signature
    if not verify_webhook_signature(body, headers):
        logger.warning("Webhook signature verification failed")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature",
        )

    # Parse the event

    try:
        event = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload",
        )

    event_type = event.get("type", "")
    event_data = event.get("data", {})

    logger.info("Processing Clerk webhook: %s", event_type)

    if event_type == "user.created" or event_type == "user.updated":
        user_service.upsert_from_webhook(db, event_data)

    elif event_type == "user.deleted":
        clerk_id = event_data.get("id", "")
        if clerk_id:
            user_service.deactivate_user(db, clerk_id)

    else:
        logger.debug("Ignoring unhandled webhook event: %s", event_type)

    return {"status": "ok"}
