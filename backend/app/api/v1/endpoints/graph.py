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

from app.api.deps import get_current_active_user, get_current_user_optional
from app.db.session import get_db
from app.models.user import User
from app.schemas.graph import (
    CommunityRead,
    ExamGistResponse,
    GlobalSearchRequest,
    LearningPathResponse,
    LearningPathStep,
    LocalSearchRequest,
    NodeDossierResponse,
    StudyChapterRead,
    StudyMapResponse,
    StudySectionRead,
    StudySubtopicRead,
    StudyTopicRead,
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

SEED_RESEARCH_GRAPH = {
    "nodes": [
        {"id": "vaswani-attention", "name": "Attention Is All You Need", "type": "PAPER", "description": "The seminal 2017 paper proposing the Transformer architecture based solely on attention mechanisms.", "level": 5, "path_order": 1},
        {"id": "self-attention", "name": "Self-Attention Mechanism", "type": "CONCEPT", "description": "Relates different positions of a single sequence to compute a contextual representation.", "level": 4, "path_order": 2},
        {"id": "scaled-dot-product", "name": "Scaled Dot-Product", "type": "CONCEPT", "description": "Attention(Q, K, V) = softmax(QK^T / sqrt(d_k))V.", "level": 3, "path_order": 3},
        {"id": "multi-head-attention", "name": "Multi-Head Attention", "type": "CONCEPT", "description": "Projects queries, keys, and values into parallel subspaces.", "level": 4, "path_order": 4},
        {"id": "positional-encoding", "name": "Positional Encoding", "type": "CONCEPT", "description": "Sinusoidal functions injecting sequence order into permutation-invariant representations.", "level": 3, "path_order": 5},
        {"id": "transformer-encoder", "name": "Transformer Encoder", "type": "SYSTEM", "description": "Stack of 6 identical layers with Multi-Head Attention and Feed-Forward sublayers.", "level": 4, "path_order": 6},
        {"id": "transformer-decoder", "name": "Transformer Decoder", "type": "SYSTEM", "description": "Stack of 6 identical layers with masked Multi-Head Attention and encoder-decoder cross-attention.", "level": 4, "path_order": 7},
        {"id": "cross-source-bert", "name": "BERT Pretraining", "type": "CONCEPT", "description": "Bidirectional encoder representations built directly on the Transformer architecture.", "level": 2, "path_order": 8},
    ],
    "edges": [
        {"source": "vaswani-attention", "target": "self-attention", "relation": "INTRODUCES", "description": "Proposes attention primitive"},
        {"source": "self-attention", "target": "scaled-dot-product", "relation": "COMPUTES_VIA", "description": "Mathematical formula"},
        {"source": "scaled-dot-product", "target": "multi-head-attention", "relation": "PROJECTS_INTO", "description": "Parallel subspace expansion"},
        {"source": "multi-head-attention", "target": "positional-encoding", "relation": "COMBINES_WITH", "description": "Sequence order injection"},
        {"source": "positional-encoding", "target": "transformer-encoder", "relation": "FEEDS_INTO", "description": "Input representation"},
        {"source": "transformer-encoder", "target": "transformer-decoder", "relation": "CONNECTS_TO", "description": "Cross-attention keys and values"},
        {"source": "transformer-encoder", "target": "cross-source-bert", "relation": "INSPIRES", "description": "Pretrained language modeling"},
    ],
}

SEED_STUDY_GRAPH = {
    "chapters": [
        {
            "id": "chap-1",
            "title": "Virtualization",
            "chapter_number": 1,
            "sections": [
                {
                    "id": "sec-1-1",
                    "title": "Process API",
                    "summary": "Core system calls: fork(), exec(), and wait().",
                    "topics": [
                        {"id": "top-1-1-1", "name": "Fork Call", "summary": "Process duplication mechanism."},
                        {"id": "top-1-1-2", "name": "Context Switch", "summary": "Kernel register swapping."},
                    ],
                }
            ],
        },
        {
            "id": "chap-2",
            "title": "Concurrency",
            "chapter_number": 2,
            "sections": [
                {
                    "id": "sec-2-1",
                    "title": "Locks & Mutexes",
                    "summary": "Mutual exclusion primitives.",
                    "topics": [
                        {"id": "top-2-1-1", "name": "Compare-And-Swap", "summary": "Hardware atomic instruction."},
                        {"id": "top-ext-paper", "name": "Amdahl Law", "summary": "Parallel speedup limits."},
                    ],
                }
            ],
        },
    ],
    "nodes": [
        {"id": "sec-1-1", "name": "Process API", "type": "SECTION", "description": "Core system calls: fork(), exec(), and wait().", "level": 4, "path_order": 1},
        {"id": "top-1-1-1", "name": "Fork Call", "type": "TOPIC", "description": "Process duplication mechanism.", "level": 3, "path_order": 2},
        {"id": "top-1-1-2", "name": "Context Switch", "type": "TOPIC", "description": "Kernel register swapping.", "level": 3, "path_order": 3},
        {"id": "chap-2", "name": "Concurrency", "type": "CHAPTER", "description": "Multi-threaded access to shared variables.", "level": 5, "path_order": 4},
        {"id": "sec-2-1", "name": "Locks & Mutexes", "type": "SECTION", "description": "Hardware and software primitives for mutual exclusion.", "level": 4, "path_order": 5},
        {"id": "top-2-1-1", "name": "Compare-And-Swap", "type": "TOPIC", "description": "Atomic hardware instruction for spinlocks.", "level": 2, "path_order": 6},
        {"id": "top-ext-paper", "name": "Amdahl Law", "type": "CONCEPT", "description": "Theoretical bound on parallel speedup.", "level": 2, "path_order": 7},
    ],
    "edges": [
        {"source": "sec-1-1", "target": "top-1-1-1", "relation": "HAS_TOPIC", "description": "Section subtopic"},
        {"source": "sec-1-1", "target": "top-1-1-2", "relation": "HAS_TOPIC", "description": "Section subtopic"},
        {"source": "top-1-1-2", "target": "chap-2", "relation": "LEADS_TO", "description": "Prerequisite milestone"},
        {"source": "chap-2", "target": "sec-2-1", "relation": "CONTAINS", "description": "Chapter section"},
        {"source": "sec-2-1", "target": "top-2-1-1", "relation": "HAS_TOPIC", "description": "Section subtopic"},
        {"source": "top-2-1-1", "target": "top-ext-paper", "relation": "NEEDS_CONTEXT", "description": "Cross-domain reference"},
    ],
}


def _verify_document_access(
    db: Session, document_id: str, user_id: uuid.UUID | None
) -> None:
    """Ensure document exists and belongs to the user (if non-demo UUID and user authenticated)."""
    if not user_id:
        return
    if document_id in ("doc-attention-1706", "doc-ostep-book", "doc-1", "default-doc"):
        return
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
        pass


@router.get("/{document_id}/town", response_model=TownGraphResponse)
def get_town_graph(
    document_id: str,
    current_user: Annotated[User | None, Depends(get_current_user_optional)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Retrieve nodes and edges for the isometric Knowledge Town graph (Research Mode).
    Seamlessly falls back to canonical flagship seed data when Neo4j is offline or empty.
    """
    _verify_document_access(db, document_id, current_user.id if current_user else None)
    data = graph_service.get_document_town_graph(document_id)
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    if not nodes:
        nodes = SEED_RESEARCH_GRAPH["nodes"]
        edges = SEED_RESEARCH_GRAPH["edges"]

    return TownGraphResponse(
        document_id=document_id,
        nodes=nodes,
        edges=edges,
    )


@router.get("/{document_id}/study-map", response_model=StudyMapResponse)
def get_study_map_endpoint(
    document_id: str,
    current_user: Annotated[User | None, Depends(get_current_user_optional)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Retrieve textbook hierarchy (Chapter -> Section -> Topic -> Subtopic)
    and canvas graph nodes/edges (Study Mode).
    """
    _verify_document_access(db, document_id, current_user.id if current_user else None)
    data = get_study_map(document_id)
    chapters = data.get("chapters", [])
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    if not nodes:
        chapters = [StudyChapterRead.model_validate(c) for c in SEED_STUDY_GRAPH["chapters"]]
        nodes = SEED_STUDY_GRAPH["nodes"]
        edges = SEED_STUDY_GRAPH["edges"]

    return StudyMapResponse(
        document_id=document_id,
        chapters=chapters,
        nodes=nodes,
        edges=edges,
    )


@router.get("/{document_id}/communities", response_model=list[CommunityRead])
def get_communities_endpoint(
    document_id: str,
    current_user: Annotated[User | None, Depends(get_current_user_optional)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Retrieve all Leiden community clusters for a document with thematic summaries and ratings.
    """
    _verify_document_access(db, document_id, current_user.id if current_user else None)
    communities = get_communities_list(document_id)
    if not communities:
        communities = [
            CommunityRead(
                id="comm-1",
                title="Attention & Feed-Forward Sublayers",
                summary="The primary computational building blocks of Transformer architectures.",
                key_findings=["Self-Attention computes contextual embeddings in O(1) sequential steps", "Residual connections prevent vanishing gradients"],
                rating=9.5,
                member_ids=["self-attention", "scaled-dot-product", "multi-head-attention"],
                member_count=3,
            ),
            CommunityRead(
                id="comm-2",
                title="Positional Encoding & Encoders",
                summary="Sequence order injection and hierarchical representation encoding.",
                key_findings=["Sinusoidal frequencies preserve relative distances", "Stacked encoders extract multi-level syntax"],
                rating=8.9,
                member_ids=["positional-encoding", "transformer-encoder", "transformer-decoder"],
                member_count=3,
            ),
        ]
    return communities


@router.get(
    "/{document_id}/nodes/{node_id}/dossier", response_model=NodeDossierResponse
)
def get_node_dossier_endpoint(
    document_id: str,
    node_id: str,
    current_user: Annotated[User | None, Depends(get_current_user_optional)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Retrieve deep-dive dossier for a single concept/entity: attributes,
    1-hop relationship edges, and verbatim source text chunks.
    """
    _verify_document_access(db, document_id, current_user.id if current_user else None)
    data = get_node_dossier(document_id, node_id)
    return NodeDossierResponse(**data)


@router.get("/{document_id}/learning-path", response_model=LearningPathResponse)
def get_learning_path_endpoint(
    document_id: str,
    current_user: Annotated[User | None, Depends(get_current_user_optional)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Retrieve ordered pedagogical learning path with prerequisite gates and context flags.
    """
    _verify_document_access(db, document_id, current_user.id if current_user else None)
    steps = get_learning_path(document_id)
    if not steps:
        steps = [
            LearningPathStep(step_index=1, id="vaswani-attention", name="Attention Is All You Need", type="PAPER", summary="Foundational introduction to Attention mechanisms", is_interchangeable=False),
            LearningPathStep(step_index=2, id="self-attention", name="Self-Attention Mechanism", type="CONCEPT", summary="Core matrix multiplication over query, key, value projections", is_interchangeable=False),
            LearningPathStep(step_index=3, id="scaled-dot-product", name="Scaled Dot-Product", type="CONCEPT", summary="Scaling factor sqrt(d_k) prevents vanishing gradients", is_interchangeable=True),
            LearningPathStep(step_index=4, id="multi-head-attention", name="Multi-Head Attention", type="CONCEPT", summary="Parallel subspace attention projections", is_interchangeable=True),
            LearningPathStep(step_index=5, id="positional-encoding", name="Positional Encoding", type="CONCEPT", summary="Sinusoids injecting token position information", is_interchangeable=False),
            LearningPathStep(step_index=6, id="transformer-encoder", name="Transformer Encoder", type="SYSTEM", summary="N=6 stacked encoder layers with layer normalization", is_interchangeable=False),
            LearningPathStep(step_index=7, id="transformer-decoder", name="Transformer Decoder", type="SYSTEM", summary="Autoregressive generation via masked attention", is_interchangeable=False),
        ]
    return LearningPathResponse(document_id=document_id, steps=steps)


@router.get("/{document_id}/exam-gist", response_model=ExamGistResponse)
def get_exam_gist_endpoint(
    document_id: str,
    current_user: Annotated[User | None, Depends(get_current_user_optional)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Retrieve 2-minute rapid revision exam summary (high-yield concepts,
    formulas, pitfalls, likely exam questions).
    """
    _verify_document_access(db, document_id, current_user.id if current_user else None)
    data = generate_exam_gist(document_id)
    return ExamGistResponse(**data)


@router.post("/{document_id}/search/local", response_model=LocalSearchResult)
def search_local_endpoint(
    document_id: str,
    request: LocalSearchRequest,
    current_user: Annotated[User | None, Depends(get_current_user_optional)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Execute local graph search: seed entity discovery + 1-hop Neo4j subgraph expansion + verbatim chunks.
    """
    _verify_document_access(db, document_id, current_user.id if current_user else None)
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
    current_user: Annotated[User | None, Depends(get_current_user_optional)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Execute global graph search: map-reduce synthesis across Leiden community summaries.
    """
    _verify_document_access(db, document_id, current_user.id if current_user else None)
    return execute_global_search(document_id=document_id, query=request.query)
