"""
Central model imports — ensures Base.metadata knows about all tables.

Import this module before calling Base.metadata.create_all() so that
SQLAlchemy discovers every model class. Add new model imports here
as you create them (documents, chat, player_profiles, etc.).
"""

from app.db.session import Base  # noqa: F401 — re-export for convenience
from app.models.chat import ChatMessage, ChatSession  # noqa: F401
from app.models.document import Document, DocumentLink, IngestionJob  # noqa: F401
from app.models.user import User  # noqa: F401

# Future model imports (uncomment as you build them):
# from app.models.document import Document
# from app.models.chat import ChatSession, ChatMessage
# from app.models.player import PlayerProfile, Quest
