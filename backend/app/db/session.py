"""
SQLAlchemy engine, session factory, and declarative base.

Every request gets its own session via the `get_db()` dependency,
which is yielded and auto-closed after the response is sent.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


settings = get_settings()
db_url = settings.postgres_url

if db_url.startswith("sqlite"):
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},
        echo=settings.environment == "development",
    )
else:
    engine = create_engine(
        db_url,
        pool_pre_ping=True,  # verify connections are alive before using them
        echo=settings.environment == "development",
    )

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Generator[Session]:
    """
    FastAPI dependency — yields a SQLAlchemy session, auto-closes on exit.

    Usage:
        @router.get("/example")
        def my_route(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
