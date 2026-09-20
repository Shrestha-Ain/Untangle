"""
Unit and integration tests for LangGraph Ingestion Pipeline and Graph Service.
"""

import uuid
from pathlib import Path
import pytest
from unittest.mock import MagicMock, patch

from app.models.document import Document, IngestionJob
from app.models.user import User
from app.llm.prompts import (
    CommunitySummaryResult,
    ExtractedEntity,
    ExtractedRelationship,
    ExtractionResult,
)
from app.services import graph_service
from app.services.ingestion.pipeline import (
    chunk_node,
    extract_node,
    finalize_node,
    parse_node,
)
from app.tasks.ingestion import run_ingestion_pipeline
from tests.conftest import TestingSessionLocal


@pytest.fixture
def sample_text_file(tmp_path):
    f = tmp_path / "research_paper.txt"
    f.write_text(
        "Scaled Dot-Product Attention connects Query and Key matrices. "
        "Multi-Head Attention projects queries and keys h times. "
        "The Transformer relies on attention mechanisms exclusively without recurrence.",
        encoding="utf-8",
    )
    return f


def test_graph_service_upsert_and_retrieve_fallback():
    """Verify graph service handles offline Neo4j gracefully."""
    doc_id = str(uuid.uuid4())
    entities = [{"name": "Transformer", "type": "METHOD", "description": "Architecture"}]
    rels = [{"source": "Transformer", "target": "Attention", "relation": "USES", "description": "rel", "weight": 1.0}]

    nodes, edges = graph_service.upsert_research_graph(doc_id, entities, rels)
    assert nodes == 1
    assert edges == 1

    town = graph_service.get_document_town_graph(doc_id)
    assert "nodes" in town
    assert "edges" in town


def test_pipeline_nodes_step_by_step(sample_text_file):
    """Verify LangGraph individual node execution and state transitions."""
    doc_id = str(uuid.uuid4())

    # 1. Parse node
    state = {
        "document_id": doc_id,
        "source_mode": "research",
        "file_path": str(sample_text_file),
    }
    parse_res = parse_node(state)
    assert len(parse_res["pages"]) == 1
    assert "Transformer" in parse_res["pages"][0][1]

    # 2. Chunk node
    state.update(parse_res)
    chunk_res = chunk_node(state)
    assert len(chunk_res["chunks"]) > 0

    # 3. Extract node with mock structured output
    state.update(chunk_res)
    mock_result = ExtractionResult(
        entities=[
            ExtractedEntity(name="Transformer", type="METHOD", description="Attention architecture"),
            ExtractedEntity(name="Attention", type="CONCEPT", description="Core routing mechanism"),
        ],
        relationships=[
            ExtractedRelationship(source="Transformer", target="Attention", relation="INCORPORATES", description="Core component"),
        ],
    )
    with patch("app.services.ingestion.pipeline.get_extraction_model") as mock_model_provider:
        mock_runnable = MagicMock()
        mock_runnable.invoke.return_value = mock_result
        mock_model_provider.return_value.with_structured_output.return_value = mock_runnable

        extract_res = extract_node(state)
        assert len(extract_res["extracted_entities"]) == 2
        assert len(extract_res["extracted_relationships"]) == 1
        assert extract_res["towers_built"] == 2


def test_full_pipeline_run_integration(sample_text_file):
    """Verify end-to-end ingestion pipeline execution and DB status update."""
    db = TestingSessionLocal()
    user = User(clerk_id="user_ingest_test", email="ingest@research.org")
    db.add(user)
    db.commit()

    doc = Document(
        user_id=user.id,
        filename="test.txt",
        file_path=str(sample_text_file),
        source_mode="research",
        status="pending",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    job = IngestionJob(
        document_id=doc.id,
        status="pending",
        current_step="parse",
    )
    db.add(job)
    db.commit()
    doc_id = str(doc.id)
    db.close()

    mock_extract = ExtractionResult(
        entities=[ExtractedEntity(name="Attention", type="CONCEPT", description="Routing algorithm")],
        relationships=[],
    )
    mock_comm = CommunitySummaryResult(
        title="Attention Mechanisms",
        summary="Community covering self-attention.",
        key_findings=["Softmax routing"],
        rating=9.0,
    )

    with (
        patch("app.services.ingestion.pipeline.get_extraction_model") as mock_ext_m,
        patch("app.services.ingestion.pipeline.get_synthesis_model") as mock_synth_m,
    ):
        ext_runnable = MagicMock()
        ext_runnable.invoke.return_value = mock_extract
        mock_ext_m.return_value.with_structured_output.return_value = ext_runnable

        synth_runnable = MagicMock()
        synth_runnable.invoke.return_value = mock_comm
        mock_synth_m.return_value.with_structured_output.return_value = synth_runnable

        result = run_ingestion_pipeline(document_id=doc_id)
        assert result["current_step"] == "done"
        assert result["percent_complete"] == 100

    # Verify document status in DB
    verify_db = TestingSessionLocal()
    updated_doc = verify_db.query(Document).filter(Document.id == uuid.UUID(doc_id)).first()
    assert updated_doc.status == "ready"
    assert updated_doc.stats["chunk_count"] > 0
    assert updated_doc.stats["entity_count"] == 1
    verify_db.close()

