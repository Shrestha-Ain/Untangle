"""
Knowledge Graph REST endpoints for Research and Study modes.

Endpoints:
- GET  /graph/{doc_id}/town            — Isometric Town Map nodes and edges
- GET  /graph/{doc_id}/study-map       — Textbook hierarchy tree and canvas elements
- GET  /graph/{doc_id}/communities     — Leiden community cluster reports
- GET  /graph/{doc_id}/nodes/{id}/dossier — Deep-dive entity/concept dossier
- GET  /graph/{doc_id}/learning-path   — Pedagogical curriculum sequence
- GET  /graph/{doc_id}/exam-gist       — 2-minute rapid revision takeaways
- POST /graph/{doc_id}/search/local    — Seed entity discovery + subgraph expansion
- POST /graph/{doc_id}/search/global   — Community map-reduce query synthesis
"""

from __future__ import annotations

import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.graph import (
    CommunityRead,
    ExamGistResponse,
    GlobalSearchRequest,
    LearningPathResponse,
    LocalSearchRequest,
    NodeDossierResponse,
    StudyMapResponse,
    TownGraphResponse,
)
from app.services import document_service, graph_service
from app.services.retrieval.global_search import (
    GlobalSearchResult,
    execute_global_search,
)
from app.services.retrieval.local_search import LocalSearchResult, execute_local_search
from app.services.retrieval.study_features import (
    generate_exam_gist,
    get_communities_list,
    get_learning_path,
    get_node_dossier,
    get_study_map,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/graph", tags=["Knowledge Graph"])


def _verify_document_access(
    db: Session, document_id: str, user_id: uuid.UUID
) -> None:
    """Ensure document exists and belongs to the active user (if valid UUID)."""
    try:
        doc_uuid = uuid.UUID(document_id)
        doc = document_service.get_document_by_id(
            db=db, document_id=doc_uuid, user_id=user_id
        )
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )
    except ValueError:
        # Allow non-UUID string identifiers (e.g. demo docs or mock IDs)
        pass


@router.get("/{document_id}/town", response_model=TownGraphResponse)
def get_town_graph(
    document_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Retrieve nodes and edges for the isometric Knowledge Town graph (Research Mode).
    """
    _verify_document_access(db, document_id, current_user.id)
    data = graph_service.get_document_town_graph(document_id)
    return TownGraphResponse(
        document_id=document_id,
        nodes=data.get("nodes", []),
        edges=data.get("edges", []),
    )


@router.get("/{document_id}/study-map", response_model=StudyMapResponse)
def get_study_map_endpoint(
    document_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Retrieve textbook hierarchy (Chapter -> Section -> Topic -> Subtopic)
    and canvas graph nodes/edges (Study Mode).
    """
    _verify_document_access(db, document_id, current_user.id)
    data = get_study_map(document_id)
    return StudyMapResponse(
        document_id=document_id,
        chapters=data.get("chapters", []),
        nodes=data.get("nodes", []),
        edges=data.get("edges", []),
    )


@router.get("/{document_id}/communities", response_model=list[CommunityRead])
def get_communities_endpoint(
    document_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Retrieve all Leiden community clusters for a document with thematic summaries and ratings.
    """
    _verify_document_access(db, document_id, current_user.id)
    return get_communities_list(document_id)


@router.get(
    "/{document_id}/nodes/{node_id}/dossier", response_model=NodeDossierResponse
)
def get_node_dossier_endpoint(
    document_id: str,
    node_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Retrieve deep-dive dossier for a single concept/entity: attributes,
    1-hop relationship edges, and verbatim source text chunks.
    """
    _verify_document_access(db, document_id, current_user.id)
    data = get_node_dossier(document_id, node_id)
    return NodeDossierResponse(**data)


@router.get("/{document_id}/learning-path", response_model=LearningPathResponse)
def get_learning_path_endpoint(
    document_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Retrieve ordered pedagogical learning path with prerequisite gates and context flags.
    """
    _verify_document_access(db, document_id, current_user.id)
    steps = get_learning_path(document_id)
    return LearningPathResponse(document_id=document_id, steps=steps)


@router.get("/{document_id}/exam-gist", response_model=ExamGistResponse)
def get_exam_gist_endpoint(
    document_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Retrieve 2-minute rapid revision exam summary (high-yield concepts,
    formulas, pitfalls, likely exam questions).
    """
    _verify_document_access(db, document_id, current_user.id)
    data = generate_exam_gist(document_id)
    return ExamGistResponse(**data)


@router.post("/{document_id}/search/local", response_model=LocalSearchResult)
def search_local_endpoint(
    document_id: str,
    request: LocalSearchRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Execute local graph search: seed entity discovery + 1-hop Neo4j subgraph expansion + verbatim chunks.
    """
    _verify_document_access(db, document_id, current_user.id)
    return execute_local_search(
        document_id=document_id,
        query=request.query,
        top_k_seeds=request.top_k_seeds,
        top_k_chunks=request.top_k_chunks,
    )


@router.post("/{document_id}/search/global", response_model=GlobalSearchResult)
def search_global_endpoint(
    document_id: str,
    request: GlobalSearchRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Execute global graph search: map-reduce synthesis across Leiden community summaries.
    """
    _verify_document_access(db, document_id, current_user.id)
    return execute_global_search(document_id=document_id, query=request.query)
