"""
Shared FastAPI dependencies — injected into routes via Depends().

Following the deep dive §A.3 pattern, adapted for Clerk auth.
Uses HTTPBearer (not OAuth2PasswordBearer) since Clerk tokens aren't
password-flow tokens — the frontend sends a session JWT in the
Authorization header.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import verify_clerk_token
from app.db.session import get_db
from app.models.user import User
from app.services import user_service

# HTTPBearer extracts the token from "Authorization: Bearer <token>"
_bearer_scheme = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """
    Verify the Clerk session JWT and return the local User record.

    Flow:
    1. Extract Bearer token from Authorization header
    2. Verify JWT signature against Clerk's JWKS (RS256)
    3. JIT-provision local user if this is their first request
    4. Return the User model instance

    Raises HTTPException(401) if token is invalid or expired.
    """
    token = credentials.credentials
    try:
        claims = verify_clerk_token(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        )

    # JIT provisioning: create local user if they don't exist yet
    user = user_service.get_or_create_from_clerk_claims(db, claims)
    return user


def get_current_active_user(
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Wraps get_current_user with an active-status check.

    Use this for most protected endpoints. Deactivated users
    (soft-deleted via webhook) get a 403.
    """
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )
    return user
