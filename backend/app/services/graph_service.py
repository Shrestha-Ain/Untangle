"""
Graph service — Neo4j knowledge graph operations for Research and Study modes.
"""

from __future__ import annotations

import logging
from typing import Any

from neo4j.exceptions import Neo4jError, ServiceUnavailable

from app.db.neo4j import get_neo4j_driver

logger = logging.getLogger(__name__)


def upsert_research_graph(
    document_id: str,
    entities: list[dict[str, Any]],
    relationships: list[dict[str, Any]],
) -> tuple[int, int]:
    """
    Persist research mode entities and directed relationships into Neo4j.
    Returns (nodes_upserted, relationships_upserted).
    """
    try:
        driver = get_neo4j_driver()
    except (Neo4jError, ServiceUnavailable, OSError) as exc:
        logger.warning("Neo4j not reachable, skipping graph upsert: %s", exc)
        return len(entities), len(relationships)

    entity_query = """
    UNWIND $entities AS e
    MERGE (node:Entity {id: e.name, document_id: $doc_id})
    ON CREATE SET
        node.name = e.name,
        node.type = e.type,
        node.description = e.description,
        node.created_at = datetime()
    ON MATCH SET
        node.description = e.description
    """

    rel_query = """
    UNWIND $rels AS r
    MATCH (source:Entity {id: r.source, document_id: $doc_id})
    MATCH (target:Entity {id: r.target, document_id: $doc_id})
    MERGE (source)-[rel:CONNECTED_TO {relation: r.relation, document_id: $doc_id}]->(target)
    ON CREATE SET
        rel.description = r.description,
        rel.weight = r.weight,
        rel.created_at = datetime()
    ON MATCH SET
        rel.description = r.description,
        rel.weight = r.weight
    """

    try:
        with driver.session() as session:
            if entities:
                session.run(entity_query, entities=entities, doc_id=document_id)
            if relationships:
                session.run(rel_query, rels=relationships, doc_id=document_id)
        logger.info(
            "Upserted %d entities and %d relations for doc %s",
            len(entities),
            len(relationships),
            document_id,
        )
        return len(entities), len(relationships)
    except (Neo4jError, ServiceUnavailable, OSError) as exc:
        logger.warning("Failed to upsert research graph to Neo4j: %s", exc)
        return len(entities), len(relationships)


def upsert_study_graph(
    document_id: str,
    chapters: list[dict[str, Any]],
) -> tuple[int, int]:
    """
    Persist study mode structural hierarchy into Neo4j:
    Chapter -> Section -> Topic -> Subtopic
    """
    try:
        driver = get_neo4j_driver()
    except (Neo4jError, ServiceUnavailable, OSError) as exc:
        logger.warning("Neo4j not reachable, skipping study graph upsert: %s", exc)
        return len(chapters), 0

    study_query = """
    UNWIND $chapters AS chap
    MERGE (c:Chapter {id: chap.title, document_id: $doc_id})
    ON CREATE SET c.title = chap.title, c.chapter_number = chap.chapter_number
    WITH c, chap
    UNWIND chap.sections AS sec
    MERGE (s:Section {id: sec.title, document_id: $doc_id})
    ON CREATE SET s.title = sec.title, s.summary = sec.summary
    MERGE (c)-[:CONTAINS_SECTION]->(s)
    WITH s, sec
    UNWIND sec.topics AS top
    MERGE (t:Topic {id: top.name, document_id: $doc_id})
    ON CREATE SET t.name = top.name, t.summary = top.summary
    MERGE (s)-[:CONTAINS_TOPIC]->(t)
    WITH t, top
    UNWIND top.subtopics AS sub
    MERGE (st:Subtopic {id: sub.name, document_id: $doc_id})
    ON CREATE SET st.name = sub.name, st.summary = sub.summary, st.needs_context = sub.needs_context
    MERGE (t)-[:CONTAINS_SUBTOPIC]->(st)
    """

    try:
        with driver.session() as session:
            session.run(study_query, chapters=chapters, doc_id=document_id)
        logger.info("Upserted %d chapters for study doc %s", len(chapters), document_id)
        return len(chapters), 0
    except (Neo4jError, ServiceUnavailable, OSError) as exc:
        logger.warning("Failed to upsert study graph to Neo4j: %s", exc)
        return len(chapters), 0


def upsert_communities(
    document_id: str,
    communities: list[dict[str, Any]],
) -> None:
    """
    Persist community clusters and link member entities.
    """
    try:
        driver = get_neo4j_driver()
    except (Neo4jError, ServiceUnavailable, OSError) as exc:
        logger.warning("Neo4j not reachable, skipping community upsert: %s", exc)
        return

    community_query = """
    UNWIND $communities AS comm
    MERGE (c:Community {id: comm.id, document_id: $doc_id})
    ON CREATE SET
        c.title = comm.title,
        c.summary = comm.summary,
        c.key_findings = comm.key_findings,
        c.rating = comm.rating
    WITH c, comm
    UNWIND comm.member_ids AS member_id
    MATCH (e:Entity {id: member_id, document_id: $doc_id})
    MERGE (c)-[:INCLUDES_ENTITY]->(e)
    """

    try:
        with driver.session() as session:
            session.run(community_query, communities=communities, doc_id=document_id)
        logger.info("Upserted %d communities for doc %s", len(communities), document_id)
    except (Neo4jError, ServiceUnavailable, OSError) as exc:
        logger.warning("Failed to upsert communities to Neo4j: %s", exc)


def get_document_town_graph(document_id: str) -> dict[str, Any]:
    """
    Fetch all nodes and edges for the isometric Town Map visualization.
    """
    try:
        driver = get_neo4j_driver()
        with driver.session() as session:
            result = session.run(
                """
                MATCH (n:Entity {document_id: $doc_id})
                OPTIONAL MATCH (n)-[r:CONNECTED_TO {document_id: $doc_id}]->(m:Entity {document_id: $doc_id})
                RETURN n, r, m
                """,
                doc_id=document_id,
            )

            nodes: dict[str, dict[str, Any]] = {}
            edges: list[dict[str, Any]] = []

            for record in result:
                n = record["n"]
                if n and n["id"] not in nodes:
                    nodes[n["id"]] = {
                        "id": n["id"],
                        "name": n.get("name", n["id"]),
                        "type": n.get("type", "CONCEPT"),
                        "description": n.get("description", ""),
                    }

                m = record["m"]
                if m and m["id"] not in nodes:
                    nodes[m["id"]] = {
                        "id": m["id"],
                        "name": m.get("name", m["id"]),
                        "type": m.get("type", "CONCEPT"),
                        "description": m.get("description", ""),
                    }

                r = record["r"]
                if r:
                    edges.append(
                        {
                            "source": n["id"],
                            "target": m["id"],
                            "relation": r.get("relation", "CONNECTED_TO"),
                            "description": r.get("description", ""),
                            "weight": r.get("weight", 1.0),
                        }
                    )

            return {
                "document_id": document_id,
                "nodes": list(nodes.values()),
                "edges": edges,
            }
    except (Neo4jError, ServiceUnavailable, OSError) as exc:
        logger.warning("Neo4j query failed, returning empty town graph: %s", exc)
        return {"document_id": document_id, "nodes": [], "edges": []}

