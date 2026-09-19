"""
Clerk JWT verification and webhook signature validation.

This module handles:
1. Fetching and caching Clerk's JWKS (JSON Web Key Set) for RS256 verification
2. Decoding and validating Clerk session tokens
3. Verifying Clerk webhook signatures (svix)

Per the action plan Phase 1: verify the Clerk session JWT against Clerk's JWKS
endpoint via python-jose + httpx to fetch/cache JWKS.
"""

import hashlib
import hmac
import logging
import time

import httpx
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class ClerkJWKSManager:
    """
    Fetches and caches Clerk's JSON Web Key Set for JWT verification.

    The JWKS is cached in memory with a configurable TTL. If a token
    presents an unknown `kid` (key ID), the cache is force-refreshed
    once to handle Clerk key rotation gracefully.
    """

    def __init__(self, jwks_url: str, cache_ttl: int = 3600):
        self._jwks_url = jwks_url
        self._cache_ttl = cache_ttl
        self._keys: dict[str, dict] = {}
        self._last_fetched: float = 0.0

    def _is_stale(self) -> bool:
        return time.time() - self._last_fetched > self._cache_ttl

    def _fetch_jwks(self) -> None:
        """Fetch JWKS from Clerk and cache the keys by kid."""
        try:
            response = httpx.get(self._jwks_url, timeout=10.0)
            response.raise_for_status()
            jwks = response.json()
            self._keys = {key["kid"]: key for key in jwks.get("keys", [])}
            self._last_fetched = time.time()
            logger.info("Fetched %d keys from Clerk JWKS endpoint", len(self._keys))
        except httpx.HTTPError as exc:
            logger.error("Failed to fetch Clerk JWKS: %s", exc)
            # Keep stale keys if we have them, better than nothing
            if not self._keys:
                raise RuntimeError(
                    f"Cannot fetch Clerk JWKS from {self._jwks_url}"
                ) from exc

    def get_key(self, kid: str) -> dict:
        """
        Get the RSA public key for a given key ID.

        If the kid is unknown or cache is stale, re-fetches JWKS.
        """
        # Refresh if stale
        if self._is_stale() or kid not in self._keys:
            self._fetch_jwks()

        # After refresh, try again — if still missing, it's genuinely unknown
        if kid not in self._keys:
            raise ValueError(f"Unknown key ID: {kid}")

        return self._keys[kid]

    def warmup(self) -> None:
        """Pre-fetch JWKS at application startup."""
        if self._jwks_url:
            try:
                self._fetch_jwks()
            except (httpx.HTTPError, RuntimeError, ValueError):
                logger.warning("JWKS warmup failed — will retry on first request")


# ── Module-level singleton ────────────────────────────────────────────
_jwks_manager: ClerkJWKSManager | None = None


def get_jwks_manager() -> ClerkJWKSManager:
    """Lazy singleton for the JWKS manager."""
    global _jwks_manager
    if _jwks_manager is None:
        settings = get_settings()
        _jwks_manager = ClerkJWKSManager(settings.clerk_jwks_url)
    return _jwks_manager


def verify_clerk_token(token: str) -> dict:
    """
    Decode and verify a Clerk session JWT.

    Steps:
    1. Extract the `kid` from the unverified header
    2. Fetch the matching RSA public key from JWKS
    3. Decode with RS256, validate expiry
    4. Return the claims dict (sub, exp, iat, etc.)

    Raises:
        HTTPException-ready errors (caller should catch and convert)
    """
    try:
        # Step 1: Get unverified header to find the key ID
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        if not kid:
            raise ValueError("Token header missing 'kid'")

        # Step 2: Get the matching public key
        manager = get_jwks_manager()
        rsa_key = manager.get_key(kid)

        # Step 3: Decode and verify
        claims = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            options={
                "verify_aud": False,  # Clerk session tokens don't always set aud
                "verify_exp": True,
            },
        )

        # Step 4: Validate essential claims
        if not claims.get("sub"):
            raise ValueError("Token missing 'sub' claim")

        return claims

    except ExpiredSignatureError:
        raise ValueError("Token has expired")
    except JWTError as exc:
        raise ValueError(f"Invalid token: {exc}")


def verify_webhook_signature(payload: bytes, headers: dict[str, str]) -> bool:
    """
    Verify a Clerk/svix webhook signature.

    Clerk uses svix for webhook delivery. The signature is verified using
    HMAC-SHA256 against the webhook secret.

    Args:
        payload: Raw request body bytes
        headers: Request headers (must contain svix-id, svix-timestamp, svix-signature)

    Returns:
        True if signature is valid, False otherwise
    """
    settings = get_settings()
    secret = settings.clerk_webhook_secret

    if not secret:
        logger.warning("CLERK_WEBHOOK_SECRET not configured — skipping verification")
        return False

    svix_id = headers.get("svix-id", "")
    svix_timestamp = headers.get("svix-timestamp", "")
    svix_signature = headers.get("svix-signature", "")

    if not all([svix_id, svix_timestamp, svix_signature]):
        return False

    # Svix secret is base64-encoded with a "whsec_" prefix
    import base64

    secret = secret.removeprefix("whsec_")
    secret_bytes = base64.b64decode(secret)

    # Build the signed content: "{msg_id}.{timestamp}.{body}"
    signed_content = f"{svix_id}.{svix_timestamp}.".encode() + payload

    # Compute expected signature
    expected = hmac.new(secret_bytes, signed_content, hashlib.sha256).digest()
    expected_b64 = base64.b64encode(expected).decode()

    # Compare against all provided signatures (svix sends multiple versions)
    for sig in svix_signature.split(" "):
        # Each signature is prefixed with version, e.g. "v1,<base64>"
        parts = sig.split(",", 1)
        if (
            len(parts) == 2
            and parts[0] == "v1"
            and hmac.compare_digest(expected_b64, parts[1])
        ):
            return True

    return False
