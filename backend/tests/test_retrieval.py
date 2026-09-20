"""
Unit tests for Local Search, Global Search, and Study Features retrieval.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.services.retrieval.global_search import execute_global_search
from app.services.retrieval.local_search import execute_local_search
from app.services.retrieval.study_features import (
    generate_exam_gist,
    get_communities_list,
    get_learning_path,
    get_node_dossier,
    get_study_map,
)


def test_execute_local_search_fallback():
    """Local search executes without throwing even when external DBs are empty or fallback."""
    with patch(
        "app.services.retrieval.local_search.get_qdrant_client"
    ) as mock_qdrant, patch(
        "app.services.retrieval.local_search.get_neo4j_driver"
    ) as mock_neo4j:
        # Mock Qdrant return
        mock_client = MagicMock()
        mock_client.query_points.return_value.points = []
        mock_qdrant.return_value = mock_client

        # Mock Neo4j return
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_session
        mock_session.run.return_value = []
        mock_driver.session.return_value = mock_session
        mock_neo4j.return_value = mock_driver

        res = execute_local_search(document_id="doc-123", query="attention mechanism")

        assert res is not None
        assert isinstance(res.seed_entities, list)
        assert isinstance(res.subgraph_nodes, list)
        assert isinstance(res.subgraph_edges, list)
        assert isinstance(res.text_chunks, list)


def test_execute_global_search_empty_communities():
    """Global search returns graceful fallback when no communities exist."""
    with patch("app.services.retrieval.global_search.get_neo4j_driver") as mock_neo4j:
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_session
        mock_session.run.return_value = []
        mock_driver.session.return_value = mock_session
        mock_neo4j.return_value = mock_driver

        res = execute_global_search(document_id="doc-123", query="main themes")
        assert res.query == "main themes"
        assert res.communities_used == []
        assert "No community reports" in res.answer


def test_execute_global_search_with_communities():
    """Global search synthesizes answer when communities exist."""
    with patch("app.services.retrieval.global_search.get_neo4j_driver") as mock_neo4j, patch(
        "app.services.retrieval.global_search.get_synthesis_model"
    ) as mock_model:
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_session
        mock_session.run.return_value = [
            {
                "id": 1,
                "title": "Neural Architectures",
                "summary": "Focuses on transformer layers and attention.",
                "key_findings": ["Self-attention scales quadratically", "Feedforward layers dominate parameters"],
                "rating": 9.0,
            }
        ]
        mock_driver.session.return_value = mock_session
        mock_neo4j.return_value = mock_driver

        # Mock LLM
        mock_llm = MagicMock()
        mock_llm.invoke.return_value.content = "Synthesized global summary of neural architectures."
        mock_model.return_value = mock_llm

        res = execute_global_search(document_id="doc-123", query="What are the key architectures?")
        assert len(res.communities_used) == 1
        assert "Synthesized global summary" in res.answer
        assert len(res.key_findings) == 2


def test_get_study_map():
    """Study map correctly builds tree and flat canvas structures."""
    with patch("app.services.retrieval.study_features.get_neo4j_driver") as mock_neo4j:
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_session
        mock_session.run.return_value = [
            {
                "c": {"id": "chap-1", "title": "Introduction", "chapter_number": 1},
                "s": {"id": "sec-1.1", "title": "Overview", "summary": "Section overview"},
                "t": {"id": "top-1", "name": "Basic Linear Algebra", "summary": "Vectors & Matrices"},
                "st": {"id": "sub-1", "name": "Vector Spaces", "summary": "Definition of spaces", "needs_context": False},
            }
        ]
        mock_driver.session.return_value = mock_session
        mock_neo4j.return_value = mock_driver

        data = get_study_map("doc-123")
        assert data["document_id"] == "doc-123"
        assert len(data["chapters"]) == 1
        assert data["chapters"][0]["title"] == "Introduction"
        assert len(data["nodes"]) == 4  # chap, sec, topic, subtopic
        assert len(data["edges"]) == 3


def test_get_learning_path():
    """Learning path returns sequential steps with prerequisite linkages."""
    with patch("app.services.retrieval.study_features.get_neo4j_driver") as mock_neo4j:
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_session
        mock_session.run.return_value = [
            {
                "c": {"id": "chap-1", "title": "Basics", "chapter_number": 1},
                "s": {"id": "sec-1", "title": "Math"},
                "t": {"id": "Matrices", "name": "Matrices", "summary": "Matrix operations"},
                "st": None,
            },
            {
                "c": {"id": "chap-1", "title": "Basics", "chapter_number": 1},
                "s": {"id": "sec-1", "title": "Math"},
                "t": {"id": "Eigenvalues", "name": "Eigenvalues", "summary": "Spectral theory"},
                "st": None,
            },
        ]
        mock_driver.session.return_value = mock_session
        mock_neo4j.return_value = mock_driver

        steps = get_learning_path("doc-123")
        assert len(steps) == 2
        assert steps[0]["name"] == "Matrices"
        assert steps[1]["name"] == "Eigenvalues"
        assert "Matrices" in steps[1]["prerequisites"]


def test_get_node_dossier():
    """Node dossier aggregates node attributes, edges, and chunks."""
    with patch("app.services.retrieval.study_features.get_neo4j_driver") as mock_neo4j, patch(
        "app.services.retrieval.study_features.get_qdrant_client"
    ) as mock_qdrant:
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_session

        # Mock single() for node info
        node_rec = MagicMock()
        node_rec.__getitem__.side_effect = lambda k: {"id": "Transformer", "name": "Transformer", "type": "CONCEPT", "description": "Sequence model"}
        mock_session.run.return_value.single.return_value = node_rec

        mock_driver.session.return_value = mock_session
        mock_neo4j.return_value = mock_driver

        # Mock Qdrant chunks
        mock_client = MagicMock()
        mock_client.query_points.return_value.points = []
        mock_qdrant.return_value = mock_client

        dossier = get_node_dossier(document_id="doc-123", node_id="Transformer")
        assert dossier["node_id"] == "Transformer"
        assert dossier["name"] == "Transformer"
        assert isinstance(dossier["incoming_relations"], list)
        assert isinstance(dossier["outgoing_relations"], list)
        assert isinstance(dossier["text_chunks"], list)


def test_get_communities_list():
    """Communities list aggregates member entity IDs."""
    with patch("app.services.retrieval.study_features.get_neo4j_driver") as mock_neo4j:
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_session
        mock_session.run.return_value = [
            {
                "id": 1,
                "title": "NLP Cluster",
                "summary": "Attention models",
                "key_findings": ["Transformers win"],
                "rating": 9.5,
                "member_ids": ["Transformer", "Attention"],
            }
        ]
        mock_driver.session.return_value = mock_session
        mock_neo4j.return_value = mock_driver

        comms = get_communities_list("doc-123")
        assert len(comms) == 1
        assert comms[0]["title"] == "NLP Cluster"
        assert comms[0]["member_count"] == 2


def test_generate_exam_gist_fallback():
    """Exam gist generates structured takeaway even under fallback."""
    with patch("app.services.retrieval.study_features.get_neo4j_driver") as mock_neo4j, patch(
        "app.services.retrieval.study_features.get_synthesis_model"
    ) as mock_model:
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_session
        mock_session.run.return_value = [
            {"name": "Backpropagation", "summary": "Gradient computation algorithm"}
        ]
        mock_driver.session.return_value = mock_session
        mock_neo4j.return_value = mock_driver

        # Trigger fallback by raising error in model
        mock_model.side_effect = RuntimeError("Model offline")

        res = generate_exam_gist("doc-123")
        assert res["document_id"] == "doc-123"
        assert "Backpropagation" in res["top_concepts"]
        assert len(res["key_formulas"]) > 0
        assert len(res["common_pitfalls"]) > 0
        assert len(res["likely_questions"]) > 0

