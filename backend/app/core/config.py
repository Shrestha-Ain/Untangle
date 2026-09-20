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
    # ── LLM & AI Providers ────────────────────────────────────────────
    gemini_api_key: str = ""
    groq_api_key: str = ""
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # ── App / CORS ────────────────────────────────────────────────────
    # Models (Defaulting to Phase 0 decisions)
    extraction_model: str = "gemini-3.5-flash-lite"
    extraction_model_fallback: str = "gemini-2.5-flash-lite"
    synthesis_model: str = "gemini-3.5-flash"
    synthesis_model_fallback: str = "llama-3.3-70b-versatile"
    chat_model: str = "llama-3.3-70b-versatile"
    chat_model_fallback: str = "gemini-3.5-flash"

    # Embeddings (Local FastEmbed)
    embedding_provider: str = "fastembed"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embedding_dim: int = 384

    # ── Storage / App / CORS ──────────────────────────────────────────
    upload_dir: str = "uploads"
    project_name: str = "Untangle"
    environment: str = "development"
    cors_origins: list[str] = ["http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    """Singleton settings instance, cached after first call."""
    return Settings()
