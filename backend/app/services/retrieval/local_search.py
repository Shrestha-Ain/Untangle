"""
Local search retrieval service — seed entity discovery via Qdrant + k-hop Neo4j subgraph expansion.
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel, Field
from qdrant_client.http.exceptions import ApiException
from qdrant_client.http.models import FieldCondition, Filter, MatchValue
from neo4j.exceptions import Neo4jError, ServiceUnavailable

from app.db.neo4j import get_neo4j_driver
from app.db.qdrant import CHUNKS_COLLECTION, ENTITIES_COLLECTION, get_qdrant_client
from app.llm.embeddings import get_embedding_service

logger = logging.getLogger(__name__)


class LocalSearchResult(BaseModel):
    """Encapsulates retrieved subgraph context and verbatim grounding chunks."""

    seed_entities: list[dict[str, Any]] = Field(default_factory=list)
    subgraph_nodes: list[dict[str, Any]] = Field(default_factory=list)
    subgraph_edges: list[dict[str, Any]] = Field(default_factory=list)
    text_chunks: list[dict[str, Any]] = Field(default_factory=list)


def execute_local_search(
    document_id: str,
    query: str,
    top_k_seeds: int = 5,
    top_k_chunks: int = 4,
) -> LocalSearchResult:
    """
    1. Embed query with local FastEmbed (384 dims).
    2. Search Qdrant entities to find top seed entities.
    3. Traverse 1-hop neighborhood in Neo4j from seeds.
    4. Retrieve top semantically relevant text chunks from Qdrant.
    """
    embedding_service = get_embedding_service()
    query_vector = embedding_service.embed_query(query)

    seed_names: list[str] = []
    seed_entities: list[dict[str, Any]] = []
    chunks: list[dict[str, Any]] = []

    # 1 & 2. Search Qdrant for seed entities and chunks
    try:
        qdrant = get_qdrant_client()
        doc_filter = Filter(
            must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]
        )

        # Query entities
        ent_hits = qdrant.query_points(
            collection_name=ENTITIES_COLLECTION,
            query=query_vector,
            query_filter=doc_filter,
            limit=top_k_seeds,
        ).points

        for h in ent_hits:
            if h.payload:
                name = h.payload.get("name", "")
                if name:
                    seed_names.append(name)
                    seed_entities.append(
                        {
                            "name": name,
                            "type": h.payload.get("type", "CONCEPT"),
                            "description": h.payload.get("description", ""),
                            "score": h.score,
                        }
                    )

        # Query text chunks
        chunk_hits = qdrant.query_points(
            collection_name=CHUNKS_COLLECTION,
            query=query_vector,
            query_filter=doc_filter,
            limit=top_k_chunks,
        ).points

        for ch in chunk_hits:
            if ch.payload:
                chunks.append(
                    {
                        "chunk_index": ch.payload.get("chunk_index"),
                        "page_number": ch.payload.get("page_number"),
                        "text": ch.payload.get("text", ""),
                        "score": ch.score,
                    }
                )

    except (ApiException, OSError, RuntimeError, ValueError) as exc:
        logger.warning("Qdrant search skipped/fallback in local search: %s", exc)

    # 3. Neo4j k-hop subgraph expansion
    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, Any]] = []

    # Add seed entities to node list
    for s in seed_entities:
        nodes[s["name"]] = {
            "id": s["name"],
            "name": s["name"],
            "type": s["type"],
            "description": s["description"],
            "is_seed": True,
        }

    try:
        if seed_names:
            driver = get_neo4j_driver()
            cypher = """
            MATCH (s:Entity {document_id: $doc_id})
            WHERE s.name IN $seed_names
            OPTIONAL MATCH (s)-[r:CONNECTED_TO {document_id: $doc_id}]-(t:Entity {document_id: $doc_id})
            RETURN s, r, t
            LIMIT 30
            """
            with driver.session() as session:
                res = session.run(cypher, doc_id=document_id, seed_names=seed_names)
                for record in res:
                    s_node = record["s"]
                    t_node = record["t"]
                    rel = record["r"]

                    if s_node and s_node["id"] not in nodes:
                        nodes[s_node["id"]] = {
                            "id": s_node["id"],
                            "name": s_node.get("name", s_node["id"]),
                            "type": s_node.get("type", "CONCEPT"),
                            "description": s_node.get("description", ""),
                            "is_seed": True,
                        }

                    if t_node and t_node["id"] not in nodes:
                        nodes[t_node["id"]] = {
                            "id": t_node["id"],
                            "name": t_node.get("name", t_node["id"]),
                            "type": t_node.get("type", "CONCEPT"),
                            "description": t_node.get("description", ""),
                            "is_seed": False,
                        }

                    if rel and s_node and t_node:
                        edges.append(
                            {
                                "source": s_node["id"],
                                "target": t_node["id"],
                                "relation": rel.get("relation", "CONNECTED_TO"),
                                "description": rel.get("description", ""),
                                "weight": rel.get("weight", 1.0),
                            }
                        )

    except (Neo4jError, ServiceUnavailable, OSError) as exc:
        logger.warning("Neo4j subgraph expansion skipped/fallback: %s", exc)

    return LocalSearchResult(
        seed_entities=seed_entities,
        subgraph_nodes=list(nodes.values()),
        subgraph_edges=edges,
        text_chunks=chunks,
    )

