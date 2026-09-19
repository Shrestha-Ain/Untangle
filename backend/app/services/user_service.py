"""
User service — business logic for user management.

Handles JIT (Just-In-Time) provisioning from Clerk JWT claims,
and full sync from Clerk webhook payloads. Follows the "thin router,
fat service" pattern from the implementation deep dive.
"""

import logging

from sqlalchemy.orm import Session

from app.models.user import User

logger = logging.getLogger(__name__)


def get_by_clerk_id(db: Session, clerk_id: str) -> User | None:
    """Look up a local user by their Clerk user ID."""
    return db.query(User).filter(User.clerk_id == clerk_id).first()


def get_or_create_from_clerk_claims(db: Session, claims: dict) -> User:
    """
    JIT provisioning: find or create a local user from Clerk JWT claims.

    On the first authenticated request from a new Clerk user, this creates
    a stub record in PostgreSQL. Subsequent requests find the existing row.

    The JWT `sub` claim is the Clerk user_id (e.g. "user_2abc...").
    """
    clerk_id = claims["sub"]
    user = get_by_clerk_id(db, clerk_id)

    if user is None:
        logger.info("JIT provisioning new user: %s", clerk_id)
        user = User(clerk_id=clerk_id)
        db.add(user)
        db.commit()
        db.refresh(user)

    return user


def upsert_from_webhook(db: Session, clerk_user_data: dict) -> User:
    """
    Create or update a local user from a Clerk webhook payload.

    Called on `user.created` and `user.updated` webhook events. The webhook
    payload contains the full user object from Clerk with fields like:
    - id: "user_2abc..."
    - email_addresses: [{email_address: "..."}]
    - first_name, last_name, image_url
    """
    clerk_id = clerk_user_data.get("id", "")
    user = get_by_clerk_id(db, clerk_id)

    # Extract email from Clerk's nested structure
    email = None
    email_addresses = clerk_user_data.get("email_addresses", [])
    if email_addresses:
        # Use the primary email, or the first one
        primary = next(
            (
                e
                for e in email_addresses
                if e.get("id") == clerk_user_data.get("primary_email_address_id")
            ),
            email_addresses[0],
        )
        email = primary.get("email_address")

    if user is None:
        logger.info("Webhook: creating user %s", clerk_id)
        user = User(
            clerk_id=clerk_id,
            email=email,
            first_name=clerk_user_data.get("first_name"),
            last_name=clerk_user_data.get("last_name"),
            image_url=clerk_user_data.get("image_url"),
        )
        db.add(user)
    else:
        logger.info("Webhook: updating user %s", clerk_id)
        if email is not None:
            user.email = email
        if clerk_user_data.get("first_name") is not None:
            user.first_name = clerk_user_data["first_name"]
        if clerk_user_data.get("last_name") is not None:
            user.last_name = clerk_user_data["last_name"]
        if clerk_user_data.get("image_url") is not None:
            user.image_url = clerk_user_data["image_url"]

    db.commit()
    db.refresh(user)
    return user


def deactivate_user(db: Session, clerk_id: str) -> None:
    """
    Soft-delete a user on `user.deleted` webhook event.

    We don't hard-delete because the user may have documents, chat history,
    and gamification data that reference them. Deactivation prevents new
    logins while preserving data integrity.
    """
    user = get_by_clerk_id(db, clerk_id)
    if user:
        logger.info("Webhook: deactivating user %s", clerk_id)
        user.is_active = False
        db.commit()
