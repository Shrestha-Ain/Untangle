"""
Neo4j driver connection manager, session provider, and schema initializers.

Handles knowledge graph storage for both Research Mode (Entities, Relationships,
Communities) and Study Mode (Chapter/Section/Topic/Subtopic hierarchy).
"""

from __future__ import annotations

import logging
from collections.abc import Generator
from contextlib import contextmanager

from neo4j import Driver, GraphDatabase, Session
from neo4j.exceptions import Neo4jError, ServiceUnavailable

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_driver: Driver | None = None


def get_neo4j_driver() -> Driver:
    """Lazy singleton for the Neo4j driver."""
    global _driver
    if _driver is None:
        settings = get_settings()
        logger.info("Initializing Neo4j driver for %s", settings.neo4j_uri)
        _driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
    return _driver


def close_neo4j_driver() -> None:
    """Closes the Neo4j driver connection pool."""
    global _driver
    if _driver is not None:
        logger.info("Closing Neo4j driver connection pool")
        _driver.close()
        _driver = None


@contextmanager
def neo4j_session_scope() -> Generator[Session]:
    """Context manager for obtaining a Neo4j session."""
    driver = get_neo4j_driver()
    session = driver.session()
    try:
        yield session
    finally:
        session.close()


def get_neo4j_session() -> Generator[Session]:
    """
    FastAPI dependency yielding a Neo4j session, auto-closed after response.
    """
    with neo4j_session_scope() as session:
        yield session


def init_neo4j_schema(driver: Driver | None = None) -> None:
    """
    Ensures unique constraints and search indexes exist in Neo4j.
    Safe to run repeatedly (uses IF NOT EXISTS).
    """
    if driver is None:
        try:
            driver = get_neo4j_driver()
            # Verify connectivity before running schema migrations
            driver.verify_connectivity()
        except (Neo4jError, ServiceUnavailable, OSError) as exc:
            logger.warning(
                "Neo4j connectivity check deferred (Neo4j not reachable yet): %s", exc
            )
            return

    statements = [
        # Constraints: composite uniqueness on (id, document_id)
        """
        CREATE CONSTRAINT entity_id_doc_unique IF NOT EXISTS
        FOR (e:Entity) REQUIRE (e.id, e.document_id) IS UNIQUE
        """,
        """
        CREATE CONSTRAINT topic_id_doc_unique IF NOT EXISTS
        FOR (t:Topic) REQUIRE (t.id, t.document_id) IS UNIQUE
        """,
        """
        CREATE CONSTRAINT chunk_id_doc_unique IF NOT EXISTS
        FOR (c:Chunk) REQUIRE (c.id, c.document_id) IS UNIQUE
        """,
        """
        CREATE CONSTRAINT community_id_doc_unique IF NOT EXISTS
        FOR (cm:Community) REQUIRE (cm.id, cm.document_id) IS UNIQUE
        """,
        # Indexes for fast lookup
        """
        CREATE INDEX entity_name_idx IF NOT EXISTS
        FOR (e:Entity) ON (e.name)
        """,
        """
        CREATE INDEX topic_name_idx IF NOT EXISTS
        FOR (t:Topic) ON (t.name)
        """,
        """
        CREATE INDEX chunk_index_idx IF NOT EXISTS
        FOR (c:Chunk) ON (c.document_id, c.chunk_index)
        """,
    ]

    try:
        with driver.session() as session:
            for stmt in statements:
                session.run(stmt)
        logger.info("Neo4j constraints and indexes successfully initialized")
    except (Neo4jError, ServiceUnavailable, OSError) as exc:
        logger.warning("Failed to initialize Neo4j schema: %s", exc)
