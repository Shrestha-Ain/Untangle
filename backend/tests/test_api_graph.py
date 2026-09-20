"""
Integration tests for Knowledge Graph REST API endpoints.
"""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_current_active_user
from app.main import app
from app.models.document import Document
from app.models.user import User
from tests.conftest import TestingSessionLocal

test_user = User(
    id=uuid.UUID("22222222-2222-2222-2222-222222222222"),
    clerk_id="user_test_graph_owner",
    email="graph_owner@untangle.ai",
    is_active=True,
)

test_doc_id = uuid.UUID("33333333-3333-3333-3333-333333333333")


def override_get_current_active_user():
    return test_user


@pytest.fixture(autouse=True)
def setup_test_data():
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user
    db = TestingSessionLocal()
    db.merge(test_user)

    # Seed test document
    doc = Document(
        id=test_doc_id,
        user_id=test_user.id,
        filename="attention_paper.pdf",
        file_path="uploads/attention_paper.pdf",
        file_size=1024,
        source_mode="research",
        status="ready",
        stats={"chunk_count": 5, "entity_count": 10},
    )
    db.merge(doc)
    db.commit()
    db.close()
    yield
    app.dependency_overrides.pop(get_current_active_user, None)


@pytest.fixture
def client():
    return TestClient(app)


def test_get_town_graph_404(client):
    """Calling /town for nonexistent document returns 404."""
    random_id = uuid.uuid4()
    resp = client.get(f"/api/v1/graph/{random_id}/town")
    assert resp.status_code == 404


def test_get_town_graph_success(client):
    """Calling /town for existing document returns town graph payload."""
    with patch("app.services.graph_service.get_document_town_graph") as mock_town:
        mock_town.return_value = {
            "document_id": str(test_doc_id),
            "nodes": [
                {"id": "Transformer", "name": "Transformer", "type": "CONCEPT", "description": "Model architecture"}
            ],
            "edges": [],
        }

        resp = client.get(f"/api/v1/graph/{test_doc_id}/town")
        assert resp.status_code == 200
        body = resp.json()
        assert body["document_id"] == str(test_doc_id)
        assert len(body["nodes"]) == 1
        assert body["nodes"][0]["name"] == "Transformer"


def test_get_study_map_success(client):
    """Calling /study-map returns chapter/section/topic curriculum."""
    with patch("app.api.v1.endpoints.graph.get_study_map") as mock_map:
        mock_map.return_value = {
            "chapters": [
                {
                    "id": "c1",
                    "title": "Deep Learning",
                    "chapter_number": 1,
                    "sections": [],
                }
            ],
            "nodes": [],
            "edges": [],
        }

        resp = client.get(f"/api/v1/graph/{test_doc_id}/study-map")
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["chapters"]) == 1
        assert body["chapters"][0]["title"] == "Deep Learning"


def test_get_communities_success(client):
    """Calling /communities returns cluster reports."""
    with patch("app.api.v1.endpoints.graph.get_communities_list") as mock_comm:
        mock_comm.return_value = [
            {
                "id": 1,
                "title": "Generative Pretraining",
                "summary": "Covers LLM pretraining mechanisms.",
                "key_findings": ["Scaling laws hold"],
                "rating": 9.2,
                "member_ids": ["GPT", "Decoder"],
                "member_count": 2,
            }
        ]

        resp = client.get(f"/api/v1/graph/{test_doc_id}/communities")
        assert resp.status_code == 200
        body = resp.json()
        assert len(body) == 1
        assert body[0]["title"] == "Generative Pretraining"
        assert body[0]["member_count"] == 2


def test_get_node_dossier_success(client):
    """Calling /nodes/{id}/dossier returns complete reading dossier."""
    with patch("app.api.v1.endpoints.graph.get_node_dossier") as mock_dossier:
        mock_dossier.return_value = {
            "node_id": "MultiHeadAttention",
            "name": "Multi-Head Attention",
            "type": "CONCEPT",
            "description": "Parallel attention mechanism.",
            "incoming_relations": [],
            "outgoing_relations": [],
            "text_chunks": [{"chunk_index": 0, "text": "We propose Multi-Head Attention...", "score": 0.95}],
        }

        resp = client.get(f"/api/v1/graph/{test_doc_id}/nodes/MultiHeadAttention/dossier")
        assert resp.status_code == 200
        body = resp.json()
        assert body["node_id"] == "MultiHeadAttention"
        assert len(body["text_chunks"]) == 1


def test_get_learning_path_success(client):
    """Calling /learning-path returns ordered curriculum steps."""
    with patch("app.api.v1.endpoints.graph.get_learning_path") as mock_lp:
        mock_lp.return_value = [
            {
                "step_index": 1,
                "id": "t1",
                "name": "Attention",
                "type": "TOPIC",
                "summary": "Attention basics",
                "needs_context": False,
                "prerequisites": [],
            }
        ]

        resp = client.get(f"/api/v1/graph/{test_doc_id}/learning-path")
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["steps"]) == 1
        assert body["steps"][0]["name"] == "Attention"


def test_get_exam_gist_success(client):
    """Calling /exam-gist returns 2-minute exam summary."""
    with patch("app.api.v1.endpoints.graph.generate_exam_gist") as mock_gist:
        mock_gist.return_value = {
            "document_id": str(test_doc_id),
            "top_concepts": ["Transformers", "Self-Attention"],
            "key_formulas": ["Attention(Q,K,V) = softmax(QK^T / sqrt(d_k))V"],
            "common_pitfalls": ["Confusing cross-attention with self-attention"],
            "likely_questions": ["Explain multi-head attention projection dimensions."],
        }

        resp = client.get(f"/api/v1/graph/{test_doc_id}/exam-gist")
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["top_concepts"]) == 2
        assert len(body["key_formulas"]) == 1


def test_search_local_endpoint(client):
    """POST /search/local executes local search."""
    with patch("app.api.v1.endpoints.graph.execute_local_search") as mock_search:
        from app.services.retrieval.local_search import LocalSearchResult
        mock_search.return_value = LocalSearchResult(
            seed_entities=[{"name": "Attention", "type": "CONCEPT", "description": "core", "score": 0.9}],
            subgraph_nodes=[],
            subgraph_edges=[],
            text_chunks=[],
        )

        resp = client.post(
            f"/api/v1/graph/{test_doc_id}/search/local",
            json={"query": "how does attention work?", "top_k_seeds": 3, "top_k_chunks": 2},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["seed_entities"]) == 1


def test_search_global_endpoint(client):
    """POST /search/global executes map-reduce global search."""
    with patch("app.api.v1.endpoints.graph.execute_global_search") as mock_search:
        from app.services.retrieval.global_search import GlobalSearchResult
        mock_search.return_value = GlobalSearchResult(
            query="overarching theme",
            communities_used=[],
            answer="The primary focus of this paper is transformer architectures.",
            key_findings=["Finding A", "Finding B"],
        )

        resp = client.post(
            f"/api/v1/graph/{test_doc_id}/search/global",
            json={"query": "overarching theme"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "transformer architectures" in body["answer"]

