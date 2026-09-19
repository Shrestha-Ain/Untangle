"""
Application settings — loaded once at startup from environment variables.

Uses pydantic-settings to validate and type all config values. A misconfigured
env var fails fast here instead of silently at runtime.

Reads from .env.local first, then .env as fallback.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application configuration. Every field maps to an env var."""

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Database connections ──────────────────────────────────────────
    postgres_url: str = "postgresql://postgres:postgres@localhost:5432/graphrag"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "changeme"
    qdrant_url: str = "http://localhost:6333"
    redis_url: str = "redis://localhost:6379/0"

    # ── Clerk auth ────────────────────────────────────────────────────
    clerk_secret_key: str = ""
    clerk_jwks_url: str = ""
    clerk_webhook_secret: str = ""

    # ── LLM (stubs for future phases) ─────────────────────────────────
    llm_provider: str = "anthropic"
    anthropic_api_key: str = ""
    extraction_model: str = "claude-haiku-4-5"
    synthesis_model: str = "claude-sonnet-4-6"
    embedding_model: str = "text-embedding-3-small"

    # ── App / CORS ────────────────────────────────────────────────────
    project_name: str = "Untangle"
    environment: str = "development"
    cors_origins: list[str] = ["http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    """Singleton settings instance, cached after first call."""
    return Settings()
