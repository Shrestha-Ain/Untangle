"""
LangGraph Ingestion State Machine.

Orchestrates the multi-stage document processing pipeline:
1. Parse   (pypdf / txt)
2. Chunk   (sentence-aware sliding window)
3. Extract (entities & relations OR textbook hierarchy via LangChain structured output)
4. Embed   (local FastEmbed 384-dim vectors to Qdrant)
5. Graph   (Neo4j Cypher persistence)
6. Summary (Community synthesis & high-yield takeaways)
7. Finalize (Postgres status update & completion telemetry)
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, TypedDict

import httpx
from langgraph.graph import END, StateGraph
from qdrant_client.http.exceptions import ApiException
from qdrant_client.http.models import PointStruct
from sqlalchemy.exc import SQLAlchemyError

from app.db.qdrant import CHUNKS_COLLECTION, ENTITIES_COLLECTION, get_qdrant_client
from app.db.session import SessionLocal
from app.llm.client import get_extraction_model, get_synthesis_model
from app.llm.embeddings import get_embedding_service
from app.llm.prompts import (
    COMMUNITY_SUMMARY_PROMPT,
    EXTRACTION_PROMPT,
    STUDY_HIERARCHY_PROMPT,
    CommunitySummaryResult,
    ExtractionResult,
    StudyHierarchyResult,
)
from app.models.document import Document, IngestionJob
from app.services import graph_service
from app.services.parser import chunk_document, extract_text_from_file
from app.tasks.celery_app import publish_telemetry

logger = logging.getLogger(__name__)


class IngestionState(TypedDict, total=False):
    document_id: str
    source_mode: str
    file_path: str
    pages: list[tuple[int | None, str]]
    chunks: list[dict[str, Any]]
    extracted_entities: list[dict[str, Any]]
    extracted_relationships: list[dict[str, Any]]
    study_hierarchy: dict[str, Any] | None
    communities: list[dict[str, Any]]
    towers_built: int
    roads_laid: int
    current_step: str
    percent_complete: int
    error: str | None


def update_db_job(
    document_id: str,
    step: str,
    percent: int,
    status: str = "running",
    message: str | None = None,
    towers: int = 0,
    roads: int = 0,
) -> None:
    """Helper updating IngestionJob and Document rows in PostgreSQL."""
    db = SessionLocal()
    try:
        doc_uuid = uuid.UUID(document_id)
        job = (
            db.query(IngestionJob).filter(IngestionJob.document_id == doc_uuid).first()
        )
        if job:
            job.status = status
            job.current_step = step
            job.percent_complete = percent
            job.towers_built = towers
            job.roads_laid = roads
            if message:
                job.message = message

        doc = db.query(Document).filter(Document.id == doc_uuid).first()
        if doc and status == "completed":
            doc.status = "ready"
        elif doc and status == "failed":
            doc.status = "failed"
            doc.error_message = message

        db.commit()
    except SQLAlchemyError as exc:
        logger.warning("Failed to update IngestionJob in DB: %s", exc)
        db.rollback()
    finally:
        db.close()


# ── Pipeline Nodes ────────────────────────────────────────────────────


def parse_node(state: IngestionState) -> dict[str, Any]:
    """Node 1: Parse raw document file into text pages."""
    doc_id = state["document_id"]
    file_path = state["file_path"]
    logger.info("[%s] Step 1: Parsing file %s", doc_id, file_path)

    publish_telemetry(
        doc_id,
        {
            "current_step": "parse",
            "percent_complete": 15,
            "message": "Parsing document pages...",
        },
    )
    update_db_job(doc_id, step="parse", percent=15, message="Parsing document pages...")

    pages = extract_text_from_file(file_path)
    return {"pages": pages, "current_step": "parse", "percent_complete": 20}


def chunk_node(state: IngestionState) -> dict[str, Any]:
    """Node 2: Sentence-aware sliding-window chunking."""
    doc_id = state["document_id"]
    pages = state.get("pages", [])
    logger.info("[%s] Step 2: Chunking %d pages", doc_id, len(pages))

    publish_telemetry(
        doc_id,
        {
            "current_step": "chunk",
            "percent_complete": 30,
            "message": "Splitting into semantic chunks...",
        },
    )
    update_db_job(
        doc_id, step="chunk", percent=30, message="Splitting into semantic chunks..."
    )

    chunks = chunk_document(pages, target_tokens=550, overlap_tokens=80)
    chunk_dicts = [c.model_dump() for c in chunks]

    return {"chunks": chunk_dicts, "current_step": "chunk", "percent_complete": 35}


def extract_node(state: IngestionState) -> dict[str, Any]:
    """Node 3: Structured Knowledge Extraction via LangChain ChatModel."""
    doc_id = state["document_id"]
    mode = state.get("source_mode", "research")
    chunks = state.get("chunks", [])
    logger.info(
        "[%s] Step 3: Extracting knowledge (mode: %s, chunks: %d)",
        doc_id,
        mode,
        len(chunks),
    )

    publish_telemetry(
        doc_id,
        {
            "current_step": "extract",
            "percent_complete": 50,
            "message": "Extracting concepts & relationships...",
        },
    )
    update_db_job(
        doc_id,
        step="extract",
        percent=50,
        message="Extracting concepts & relationships...",
    )

    all_entities: dict[str, dict[str, Any]] = {}
    all_relationships: list[dict[str, Any]] = []
    study_hierarchy: dict[str, Any] | None = None

    if mode == "study":
        # Extract structural textbook hierarchy across full text sample
        joined_text = "\n\n".join([c["text"] for c in chunks[:5]])  # initial chapters
        try:
            model = get_extraction_model().with_structured_output(StudyHierarchyResult)
            prompt = STUDY_HIERARCHY_PROMPT.invoke({"text": joined_text})
            result: StudyHierarchyResult = model.invoke(prompt)
            study_hierarchy = result.model_dump()
        except (ValueError, RuntimeError) as exc:
            logger.warning("[%s] Study extraction fallback: %s", doc_id, exc)
            study_hierarchy = {"chapters": []}
    else:
        # Research Mode: Extract Entities & Relationships from chunks
        model = get_extraction_model().with_structured_output(ExtractionResult)
        for c in chunks[:10]:  # batch process initial chunks
            try:
                prompt = EXTRACTION_PROMPT.invoke({"text": c["text"]})
                res: ExtractionResult = model.invoke(prompt)
                for ent in res.entities:
                    if ent.name not in all_entities:
                        all_entities[ent.name] = ent.model_dump()
                for rel in res.relationships:
                    all_relationships.append(rel.model_dump())
            except (ValueError, RuntimeError) as exc:
                logger.debug(
                    "[%s] Extraction skipped for chunk %d: %s",
                    doc_id,
                    c["chunk_index"],
                    exc,
                )

    entities_list = list(all_entities.values())
    logger.info(
        "[%s] Extracted %d entities and %d relationships",
        doc_id,
        len(entities_list),
        len(all_relationships),
    )

    return {
        "extracted_entities": entities_list,
        "extracted_relationships": all_relationships,
        "study_hierarchy": study_hierarchy,
        "towers_built": len(entities_list),
        "roads_laid": len(all_relationships),
        "current_step": "extract",
        "percent_complete": 65,
    }


def embed_node(state: IngestionState) -> dict[str, Any]:
    """Node 4: Compute dense FastEmbed vectors and index into Qdrant."""
    doc_id = state["document_id"]
    chunks = state.get("chunks", [])
    entities = state.get("extracted_entities", [])
    logger.info(
        "[%s] Step 4: Embedding %d chunks and %d entities",
        doc_id,
        len(chunks),
        len(entities),
    )

    publish_telemetry(
        doc_id,
        {
            "current_step": "embed",
            "percent_complete": 75,
            "message": "Indexing dense semantic embeddings...",
        },
    )
    update_db_job(
        doc_id,
        step="embed",
        percent=75,
        message="Indexing dense semantic embeddings...",
    )

    try:
        embedding_service = get_embedding_service()
        qdrant = get_qdrant_client()

        # 1. Embed and index chunks
        if chunks:
            chunk_texts = [c["text"] for c in chunks]
            vectors = embedding_service.embed_documents(chunk_texts)
            points = [
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vec,
                    payload={
                        "document_id": doc_id,
                        "chunk_index": c["chunk_index"],
                        "page_number": c["page_number"],
                        "text": c["text"],
                    },
                )
                for c, vec in zip(chunks, vectors)
            ]
            qdrant.upsert(collection_name=CHUNKS_COLLECTION, points=points)

        # 2. Embed and index entities
        if entities:
            entity_texts = [f"{e['name']}: {e['description']}" for e in entities]
            ent_vectors = embedding_service.embed_documents(entity_texts)
            ent_points = [
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vec,
                    payload={
                        "document_id": doc_id,
                        "name": e["name"],
                        "type": e["type"],
                        "description": e["description"],
                    },
                )
                for e, vec in zip(entities, ent_vectors)
            ]
            qdrant.upsert(collection_name=ENTITIES_COLLECTION, points=ent_points)

    except (ApiException, httpx.HTTPError, OSError, RuntimeError, ValueError) as exc:
        logger.warning(
            "[%s] Qdrant embedding indexing skipped/deferred: %s", doc_id, exc
        )

    return {"current_step": "embed", "percent_complete": 80}


def graph_node(state: IngestionState) -> dict[str, Any]:
    """Node 5: Persist knowledge graph in Neo4j."""
    doc_id = state["document_id"]
    mode = state.get("source_mode", "research")
    entities = state.get("extracted_entities", [])
    relationships = state.get("extracted_relationships", [])
    study_hierarchy = state.get("study_hierarchy")
    logger.info("[%s] Step 5: Upserting knowledge graph to Neo4j", doc_id)

    publish_telemetry(
        doc_id,
        {
            "current_step": "cluster",
            "percent_complete": 85,
            "message": "Constructing knowledge graph towers & roads...",
        },
    )
    update_db_job(
        doc_id,
        step="cluster",
        percent=85,
        message="Constructing knowledge graph towers & roads...",
    )

    if mode == "study" and study_hierarchy and "chapters" in study_hierarchy:
        graph_service.upsert_study_graph(doc_id, study_hierarchy["chapters"])
    else:
        graph_service.upsert_research_graph(doc_id, entities, relationships)

    return {"current_step": "cluster", "percent_complete": 90}


def summarize_node(state: IngestionState) -> dict[str, Any]:
    """Node 6: Synthesize thematic community clusters via LLM."""
    doc_id = state["document_id"]
    entities = state.get("extracted_entities", [])
    logger.info("[%s] Step 6: Community clustering and thematic synthesis", doc_id)

    publish_telemetry(
        doc_id,
        {
            "current_step": "summarize",
            "percent_complete": 92,
            "message": "Synthesizing thematic communities...",
        },
    )
    update_db_job(
        doc_id,
        step="summarize",
        percent=92,
        message="Synthesizing thematic communities...",
    )

    communities: list[dict[str, Any]] = []

    if entities:
        # Create primary community for the main cluster
        cluster_members = [e["name"] for e in entities[:8]]
        cluster_text = "\n".join(
            [f"- {e['name']} ({e['type']}): {e['description']}" for e in entities[:8]]
        )

        try:
            model = get_synthesis_model().with_structured_output(CommunitySummaryResult)
            prompt = COMMUNITY_SUMMARY_PROMPT.invoke(
                {"entities_and_relationships": cluster_text}
            )
            summary_res: CommunitySummaryResult = model.invoke(prompt)

            comm_dict = {
                "id": f"{doc_id}_comm_1",
                "title": summary_res.title,
                "summary": summary_res.summary,
                "key_findings": summary_res.key_findings,
                "rating": summary_res.rating,
                "member_ids": cluster_members,
            }
            communities.append(comm_dict)
            graph_service.upsert_communities(doc_id, communities)
        except (ValueError, RuntimeError) as exc:
            logger.warning("[%s] Community synthesis fallback: %s", doc_id, exc)

    return {
        "communities": communities,
        "current_step": "summarize",
        "percent_complete": 95,
    }


def finalize_node(state: IngestionState) -> dict[str, Any]:
    """Node 7: Finalize document status in PostgreSQL and send 100% completion telemetry."""
    doc_id = state["document_id"]
    chunks = state.get("chunks", [])
    entities = state.get("extracted_entities", [])
    communities = state.get("communities", [])
    towers = state.get("towers_built", len(entities))
    roads = state.get("roads_laid", 0)

    logger.info("[%s] Step 7: Finalizing ingestion pipeline", doc_id)

    db = SessionLocal()
    try:
        doc_uuid = uuid.UUID(doc_id)
        doc = db.query(Document).filter(Document.id == doc_uuid).first()
        if doc:
            doc.status = "ready"
            doc.stats = {
                "chunk_count": len(chunks),
                "entity_count": len(entities),
                "community_count": len(communities),
                "chapter_count": 0,
            }
            db.commit()
    except SQLAlchemyError as exc:
        logger.warning("[%s] Error updating document stats: %s", doc_id, exc)
    finally:
        db.close()

    update_db_job(
        doc_id,
        step="done",
        percent=100,
        status="completed",
        message="Knowledge Map ready",
        towers=towers,
        roads=roads,
    )
    publish_telemetry(
        doc_id,
        {
            "current_step": "done",
            "percent_complete": 100,
            "status": "completed",
            "message": "Knowledge Map ready",
            "towers_built": towers,
            "roads_laid": roads,
        },
    )

    return {"current_step": "done", "percent_complete": 100}


# ── LangGraph Graph Builder ───────────────────────────────────────────


def build_ingestion_pipeline() -> StateGraph:
    """
    Constructs the LangGraph state machine workflow.
    """
    workflow = StateGraph(IngestionState)

    workflow.add_node("parse", parse_node)
    workflow.add_node("chunk", chunk_node)
    workflow.add_node("extract", extract_node)
    workflow.add_node("embed", embed_node)
    workflow.add_node("graph", graph_node)
    workflow.add_node("summarize", summarize_node)
    workflow.add_node("finalize", finalize_node)

    workflow.set_entry_point("parse")
    workflow.add_edge("parse", "chunk")
    workflow.add_edge("chunk", "extract")
    workflow.add_edge("extract", "embed")
    workflow.add_edge("embed", "graph")
    workflow.add_edge("graph", "summarize")
    workflow.add_edge("summarize", "finalize")
    workflow.add_edge("finalize", END)

    return workflow.compile()


# Compiled LangGraph pipeline application
ingestion_pipeline_app = build_ingestion_pipeline()
