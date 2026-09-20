"""
FastAPI application — entry point.

Start with: uv run uvicorn app.main:app --reload --port 8000
Docs at:    http://localhost:8000/docs

This module creates the FastAPI app, configures CORS, sets up the
database tables, and mounts the API routers. The lifespan handler
runs startup/shutdown tasks (JWKS cache warmup, table creation).
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.router import api_v1_router
from app.core.config import get_settings
from app.core.security import get_jwks_manager
from app.db.base import Base
from app.db.neo4j import close_neo4j_driver, init_neo4j_schema
from app.db.qdrant import close_qdrant_client, init_qdrant_collections
from app.db.session import engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan — runs on startup and shutdown.

    Startup:
    - Create database tables (dev convenience — use Alembic migrations in production)
    - Initialize Neo4j constraints & indexes
    - Initialize Qdrant vector collections
    - Pre-warm the Clerk JWKS cache so first auth request doesn't block

    Shutdown:
    - Cleanup resources
    - Cleanup database & driver connections
    """
    settings = get_settings()

    # ── Startup ───────────────────────────────────────────────────────
    logger.info("Starting %s (%s)", settings.project_name, settings.environment)

    # Create tables — safe to call repeatedly, only creates missing tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables ensured")
    except SQLAlchemyError as exc:
        logger.warning(
            "Database table creation deferred (PostgreSQL not reachable yet): %s", exc
        )

    # Initialize graph and vector store schemas
    init_neo4j_schema()
    init_qdrant_collections()

    # Pre-warm JWKS cache
    jwks_manager = get_jwks_manager()
    jwks_manager.warmup()

    yield

    # ── Shutdown ──────────────────────────────────────────────────────
    logger.info("Shutting down %s", settings.project_name)
    close_neo4j_driver()
    close_qdrant_client()
    engine.dispose()


def create_app() -> FastAPI:
    """Application factory."""
    settings = get_settings()

    app = FastAPI(
        title=settings.project_name,
        description="Research Realm GraphRAG Explorer — Backend API",
        version="0.1.0",
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────────────
    # Allow the Vue frontend dev server (and any configured origins)
    # to make credentialed requests to the API.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ───────────────────────────────────────────────────────
    from app.api.v1.endpoints import ws

    app.include_router(api_v1_router)
    app.include_router(ws.router)

    # ── Health check ──────────────────────────────────────────────────
    @app.get("/api/health", tags=["Health"])
    @app.get("/api/v1/health", tags=["Health"])
    def health_check():
        """Simple health check — returns 200 if the server is running."""
        return {"status": "ok"}

    return app


# Module-level app instance for uvicorn
app = create_app()
