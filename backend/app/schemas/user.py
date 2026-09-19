"""
Pydantic schemas for User data — request/response contracts.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    """Shared fields across user schemas."""

    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    image_url: str | None = None


class UserCreate(UserBase):
    """Internal schema for creating a user from Clerk data."""

    clerk_id: str


class UserUpdate(UserBase):
    """Partial update — all fields optional."""

    is_active: bool | None = None


class UserRead(UserBase):
    """Public-facing user response returned by API endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    clerk_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
