"""
Shared pytest configuration and fixtures.

Sets up global in-memory SQLite engine and FastAPI dependency overrides
so tests never touch production databases or interfere with each other.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db as deps_get_db
from app.db.base import Base
from app.db.session import SessionLocal
from app.db.session import get_db as session_get_db
from app.main import app
from app.tasks.celery_app import celery_app

SQLITE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessionLocal.configure(bind=test_engine)
TestingSessionLocal = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)

# Configure Celery in-memory broker for unit tests
celery_app.conf.update(
    broker_url="memory://",
    result_backend="cache+memory://",
    task_always_eager=False,
)


def override_get_db():
    """Yield a transactional session connected to the test SQLite database."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_test_db_and_tables():
    """Ensure in-memory SQLite and tables are ready for every single test."""
    SessionLocal.configure(bind=test_engine)
    app.dependency_overrides[session_get_db] = override_get_db
    app.dependency_overrides[deps_get_db] = override_get_db
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

