"""
v1 API router — assembles all endpoint modules under /api/v1.

Add new endpoint routers here as you build them (documents, graph, chat, player, etc.).
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, chat, documents, graph

api_v1_router = APIRouter(prefix="/api/v1")

# ── Auth ──────────────────────────────────────────────────────────────
api_v1_router.include_router(auth.router)

# ── Documents ─────────────────────────────────────────────────────────
api_v1_router.include_router(documents.router)

# ── Knowledge Graph & Retrieval ───────────────────────────────────────
api_v1_router.include_router(graph.router)

# ── Chat & Regulus AI Guide ───────────────────────────────────────────
api_v1_router.include_router(chat.router)

# ── Future endpoint routers (uncomment as you build them) ─────────────
# from app.api.v1.endpoints import documents, graph, chat, player
# api_v1_router.include_router(documents.router)
# from app.api.v1.endpoints import graph, chat
# api_v1_router.include_router(graph.router)
# api_v1_router.include_router(chat.router)
# api_v1_router.include_router(player.router)
