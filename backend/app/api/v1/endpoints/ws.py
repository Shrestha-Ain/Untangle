"""
WebSocket streaming endpoints.

- /ws/chat/{session_id}            — Token-by-token streaming response + subgraph illumination
- /ws/documents/{doc_id}/progress  — Redis pub/sub real-time ingestion telemetry
"""

from __future__ import annotations

import json
import logging
import uuid
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Query,
    WebSocket,
    WebSocketDisconnect,
    status,
)
import redis.asyncio as aioredis
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import verify_clerk_token
from app.db.session import get_db
from app.services import chat_service, document_service, user_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSockets"])
settings = get_settings()


async def _get_ws_user(token: str | None, db: Session):
    """Authenticate WebSocket connection using query token parameter."""
    if not token:
        return None
    try:
        claims = verify_clerk_token(token)
        user = user_service.get_or_create_from_clerk_claims(db, claims)
        if not user.is_active:
            return None
        return user
    except (ValueError, RuntimeError, KeyError):
        return None


@router.websocket("/ws/chat/{session_id}")
async def ws_chat_endpoint(
    websocket: WebSocket,
    session_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[str | None, Query()] = None,
):
    """
    WebSocket endpoint for interactive streaming chat with Regulus AI Guide.
    Emits token events sequentially, followed by a 'done' event with illuminated subgraph and citations.
    """
    user = await _get_ws_user(token, db)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    session = chat_service.get_chat_session(db, session_id=session_id, user_id=user.id)
    if not session:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    logger.info("WebSocket chat connection established: session=%s user=%s", session_id, user.id)

    try:
        while True:
            data = await websocket.receive_json()
            query = data.get("content") or data.get("query")
            search_mode = data.get("search_mode")

            if not query or not query.strip():
                continue

            # Stream response events
            async for event in chat_service.stream_chat_turn(
                db=db,
                session=session,
                query=query.strip(),
                search_mode=search_mode,
            ):
                await websocket.send_json(event)

    except WebSocketDisconnect:
        logger.info("WebSocket chat disconnected: session=%s", session_id)
    except (RuntimeError, OSError) as exc:
        logger.warning("WebSocket chat error: %s", exc)
        try:
            await websocket.send_json({"type": "error", "message": "An internal error occurred."})
        except (RuntimeError, OSError):
            pass


@router.websocket("/ws/documents/{document_id}/progress")
async def ws_document_progress_endpoint(
    websocket: WebSocket,
    document_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[str | None, Query()] = None,
):
    """
    WebSocket subscription to real-time ingestion telemetry for a document.
    Listens to Redis pub/sub channel `doc:{document_id}:progress`.
    """
    user = await _get_ws_user(token, db)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    doc = document_service.get_document_by_id(db, document_id=document_id, user_id=user.id)
    if not doc:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    logger.info("WebSocket progress subscription established: doc=%s", document_id)

    # Send initial state
    initial_percent = 100 if doc.status == "ready" else (0 if doc.status == "failed" else 15)
    await websocket.send_json(
        {
            "current_step": doc.status,
            "percent_complete": initial_percent,
            "message": f"Document status: {doc.status}",
        }
    )

    if doc.status in ("ready", "failed"):
        await websocket.close(code=status.WS_1000_NORMAL_CLOSURE)
        return

    channel_name = f"doc:{document_id}:progress"
    redis_client = None

    try:
        redis_client = aioredis.from_url(settings.redis_url)
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(channel_name)

        async for msg in pubsub.listen():
            if msg["type"] == "message":
                payload = json.loads(msg["data"].decode("utf-8"))
                await websocket.send_json(payload)
                if payload.get("current_step") in ("ready", "failed"):
                    break

        await pubsub.unsubscribe(channel_name)

    except WebSocketDisconnect:
        logger.info("WebSocket progress client disconnected: doc=%s", document_id)
    except (aioredis.RedisError, OSError, RuntimeError) as exc:
        logger.debug("Redis progress pub/sub subscription ended: %s", exc)
    finally:
        if redis_client:
            await redis_client.aclose()
