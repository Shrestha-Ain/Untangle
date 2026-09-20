"""
Unit & integration tests for Clerk authentication and user provisioning.

Tests:
1. /api/health endpoint
2. /api/v1/auth/me unauthenticated (401)
3. /api/v1/auth/me with valid Clerk JWT (RS256 verification + JIT user provisioning)
4. /api/v1/auth/me with expired or invalid token (401)
5. /api/v1/auth/webhook with valid svix signature (user.created, user.updated, user.deleted)
6. /api/v1/auth/webhook with invalid signature (400)
7. Deactivated user returns 403
"""

import base64
import hashlib
import hmac
import time
import uuid

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from jose import jwt

from app.core.config import get_settings
from app.core.security import get_jwks_manager
from app.main import app
from tests.conftest import TestingSessionLocal


# ── RSA Key Pair Generation for Mocking Clerk ─────────────────────────
@pytest.fixture(scope="session")
def rsa_keypair():
    """Generates an RSA keypair for signing and verifying test JWTs."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()

    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")

    pem_public = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")

    # Generate public numbers for JWKS dict format
    public_numbers = public_key.public_numbers()
    e_bytes = public_numbers.e.to_bytes(
        (public_numbers.e.bit_length() + 7) // 8, byteorder="big"
    )
    n_bytes = public_numbers.n.to_bytes(
        (public_numbers.n.bit_length() + 7) // 8, byteorder="big"
    )

    jwk_dict = {
        "kty": "RSA",
        "use": "sig",
        "alg": "RS256",
        "kid": "test_kid_1",
        "n": base64.urlsafe_b64encode(n_bytes).decode("utf-8").rstrip("="),
        "e": base64.urlsafe_b64encode(e_bytes).decode("utf-8").rstrip("="),
    }

    return {
        "private_pem": pem_private,
        "public_pem": pem_public,
        "jwk": jwk_dict,
        "kid": "test_kid_1",
    }





@pytest.fixture
def client():
    return TestClient(app)


def make_test_jwt(rsa_keypair, sub="user_2test123", expired=False):
    """Helper to create a signed Clerk-like JWT."""
    now = int(time.time())
    payload = {
        "sub": sub,
        "iat": now,
        "exp": now - 100 if expired else now + 3600,
        "iss": "https://test.clerk.accounts.dev",
        "azp": "http://localhost:5173",
    }
    headers = {"kid": rsa_keypair["kid"], "alg": "RS256"}
    return jwt.encode(
        payload, rsa_keypair["private_pem"], algorithm="RS256", headers=headers
    )


def make_svix_headers(
    payload_bytes: bytes, secret: str = "whsec_testsecret12345678901234567890"
):
    """Helper to generate valid svix webhook signature headers."""
    svix_id = f"msg_{uuid.uuid4().hex}"
    svix_timestamp = str(int(time.time()))

    # Decode secret (strip whsec_ prefix if present)
    sec = secret.removeprefix("whsec_")
    # Ensure proper base64 padding
    padded_sec = sec + "=" * ((4 - len(sec) % 4) % 4)
    secret_bytes = base64.b64decode(padded_sec)

    signed_content = f"{svix_id}.{svix_timestamp}.".encode() + payload_bytes
    signature = hmac.new(secret_bytes, signed_content, hashlib.sha256).digest()
    sig_b64 = base64.b64encode(signature).decode()

    return {
        "svix-id": svix_id,
        "svix-timestamp": svix_timestamp,
        "svix-signature": f"v1,{sig_b64}",
        "content-type": "application/json",
    }


# ── Tests ─────────────────────────────────────────────────────────────


def test_health_check(client):
    """Test public health endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_auth_me_unauthorized(client):
    """Request without token must return 401."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_auth_me_invalid_token(client):
    """Request with malformed token must return 401."""
    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer not-a-valid-token"}
    )
    assert response.status_code == 401


def test_auth_me_expired_token(client, rsa_keypair):
    """Request with expired token must return 401."""
    manager = get_jwks_manager()
    manager._keys[rsa_keypair["kid"]] = rsa_keypair["jwk"]
    manager._last_fetched = time.time()

    token = make_test_jwt(rsa_keypair, expired=True)
    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401
    assert "expired" in response.json()["detail"].lower()


def test_auth_me_jit_provisioning_and_lookup(client, rsa_keypair):
    """
    First authenticated request creates the user in DB (JIT).
    Subsequent request returns the existing user.
    """
    manager = get_jwks_manager()
    manager._keys[rsa_keypair["kid"]] = rsa_keypair["jwk"]
    manager._last_fetched = time.time()

    token = make_test_jwt(rsa_keypair, sub="user_clerk_jit_999")

    # First request: JIT provision
    response1 = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response1.status_code == 200
    data1 = response1.json()
    assert data1["clerk_id"] == "user_clerk_jit_999"
    assert data1["is_active"] is True
    user_id = data1["id"]

    # Second request: fetches same user
    response2 = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["id"] == user_id
    assert data2["clerk_id"] == "user_clerk_jit_999"


def test_clerk_webhook_lifecycle(client, monkeypatch):
    """Test webhook events: user.created, user.updated, user.deleted."""
    test_secret = "whsec_YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXoxMjM0NTY="
    monkeypatch.setattr(get_settings(), "clerk_webhook_secret", test_secret)

    # 1. Invalid signature rejection
    bad_payload = b'{"type": "user.created", "data": {}}'
    bad_headers = {
        "svix-id": "msg_123",
        "svix-timestamp": str(int(time.time())),
        "svix-signature": "v1,invalid_sig",
        "content-type": "application/json",
    }
    resp = client.post("/api/v1/auth/webhook", content=bad_payload, headers=bad_headers)
    assert resp.status_code == 400

    # 2. user.created event
    created_payload = b"""{
        "type": "user.created",
        "data": {
            "id": "user_webhook_123",
            "first_name": "Ada",
            "last_name": "Lovelace",
            "image_url": "https://example.com/ada.png",
            "primary_email_address_id": "email_1",
            "email_addresses": [
                {"id": "email_1", "email_address": "ada@example.com"}
            ]
        }
    }"""
    headers = make_svix_headers(created_payload, secret=test_secret)
    resp = client.post("/api/v1/auth/webhook", content=created_payload, headers=headers)
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}

    # 3. user.updated event
    updated_payload = b"""{
        "type": "user.updated",
        "data": {
            "id": "user_webhook_123",
            "first_name": "Lady Ada",
            "last_name": "Lovelace",
            "image_url": "https://example.com/ada_new.png",
            "primary_email_address_id": "email_1",
            "email_addresses": [
                {"id": "email_1", "email_address": "ada.updated@example.com"}
            ]
        }
    }"""
    headers = make_svix_headers(updated_payload, secret=test_secret)
    resp = client.post("/api/v1/auth/webhook", content=updated_payload, headers=headers)
    assert resp.status_code == 200

    # 4. user.deleted event (soft delete / deactivate)
    deleted_payload = b"""{
        "type": "user.deleted",
        "data": {
            "id": "user_webhook_123"
        }
    }"""
    headers = make_svix_headers(deleted_payload, secret=test_secret)
    resp = client.post("/api/v1/auth/webhook", content=deleted_payload, headers=headers)
    assert resp.status_code == 200


def test_deactivated_user_forbidden(client, rsa_keypair):
    """A deactivated user calling /me must receive 403 Forbidden."""
    manager = get_jwks_manager()
    manager._keys[rsa_keypair["kid"]] = rsa_keypair["jwk"]
    manager._last_fetched = time.time()

    # Create user via JIT first
    token = make_test_jwt(rsa_keypair, sub="user_to_deactivate")
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200

    # Deactivate the user directly in DB
    db = TestingSessionLocal()
    from app.services import user_service

    user_service.deactivate_user(db, "user_to_deactivate")
    db.close()

    # Now calling /me returns 403
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403
    assert "deactivated" in resp.json()["detail"].lower()
