"""
Study features retrieval service — Study Map, Learning Path, Node Dossier, Communities, and Exam Gist.
"""

from __future__ import annotations

import logging
from typing import Any

from neo4j.exceptions import Neo4jError, ServiceUnavailable
from qdrant_client.http.exceptions import ApiException
from qdrant_client.http.models import FieldCondition, Filter, MatchValue

from app.db.neo4j import get_neo4j_driver
from app.db.qdrant import CHUNKS_COLLECTION, get_qdrant_client
from app.llm.client import get_synthesis_model
from app.llm.embeddings import get_embedding_service
from app.llm.prompts import EXAM_GIST_PROMPT, ExamGistResult

logger = logging.getLogger(__name__)


def get_study_map(document_id: str) -> dict[str, Any]:
    """
    Retrieve textbook hierarchy (Chapter -> Section -> Topic -> Subtopic)
    and construct both a nested tree and a flat nodes/edges representation.
    """
    chapters_dict: dict[str, dict[str, Any]] = {}
    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, Any]] = []

    try:
        driver = get_neo4j_driver()
        cypher = """
        MATCH (c:Chapter {document_id: $doc_id})
        OPTIONAL MATCH (c)-[:CONTAINS_SECTION]->(s:Section {document_id: $doc_id})
        OPTIONAL MATCH (s)-[:CONTAINS_TOPIC]->(t:Topic {document_id: $doc_id})
        OPTIONAL MATCH (t)-[:CONTAINS_SUBTOPIC]->(st:Subtopic {document_id: $doc_id})
        RETURN c, s, t, st
        ORDER BY c.chapter_number, c.title, s.title, t.name, st.name
        """
        with driver.session() as session:
            result = session.run(cypher, doc_id=document_id)
            for record in result:
                c = record["c"]
                s = record["s"]
                t = record["t"]
                st = record["st"]

                if not c:
                    continue

                c_id = c["id"]
                if c_id not in chapters_dict:
                    chapters_dict[c_id] = {
                        "id": c_id,
                        "title": c.get("title", c_id),
                        "chapter_number": c.get("chapter_number"),
                        "sections": {},
                    }
                    nodes[c_id] = {
                        "id": c_id,
                        "name": c.get("title", c_id),
                        "type": "CHAPTER",
                        "description": f"Chapter {c.get('chapter_number', '')}",
                        "level": 3,
                    }

                if s:
                    s_id = s["id"]
                    if s_id not in chapters_dict[c_id]["sections"]:
                        chapters_dict[c_id]["sections"][s_id] = {
                            "id": s_id,
                            "title": s.get("title", s_id),
                            "summary": s.get("summary", ""),
                            "topics": {},
                        }
                        nodes[s_id] = {
                            "id": s_id,
                            "name": s.get("title", s_id),
                            "type": "SECTION",
                            "description": s.get("summary", ""),
                            "level": 2,
                        }
                        edges.append(
                            {
                                "source": c_id,
                                "target": s_id,
                                "relation": "CONTAINS_SECTION",
                                "description": "Chapter section",
                                "weight": 1.0,
                            }
                        )

                    if t:
                        t_id = t["id"]
                        sec_topics = chapters_dict[c_id]["sections"][s_id]["topics"]
                        if t_id not in sec_topics:
                            sec_topics[t_id] = {
                                "id": t_id,
                                "name": t.get("name", t_id),
                                "summary": t.get("summary", ""),
                                "subtopics": [],
                                "conceptually_links_to": [],
                            }
                            nodes[t_id] = {
                                "id": t_id,
                                "name": t.get("name", t_id),
                                "type": "TOPIC",
                                "description": t.get("summary", ""),
                                "level": 1,
                            }
                            edges.append(
                                {
                                    "source": s_id,
                                    "target": t_id,
                                    "relation": "CONTAINS_TOPIC",
                                    "description": "Section topic",
                                    "weight": 1.0,
                                }
                            )

                        if st:
                            st_id = st["id"]
                            sec_topics[t_id]["subtopics"].append(
                                {
                                    "id": st_id,
                                    "name": st.get("name", st_id),
                                    "summary": st.get("summary", ""),
                                    "needs_context": st.get("needs_context", False),
                                }
                            )
                            nodes[st_id] = {
                                "id": st_id,
                                "name": st.get("name", st_id),
                                "type": "SUBTOPIC",
                                "description": st.get("summary", ""),
                                "level": 0,
                            }
                            edges.append(
                                {
                                    "source": t_id,
                                    "target": st_id,
                                    "relation": "CONTAINS_SUBTOPIC",
                                    "description": "Topic subtopic",
                                    "weight": 1.0,
                                }
                            )

    except (Neo4jError, ServiceUnavailable, OSError) as exc:
        logger.warning("Neo4j study map fetch error: %s", exc)

    # Flatten nested dicts into list structures
    formatted_chapters: list[dict[str, Any]] = []
    for c_info in chapters_dict.values():
        sections_list: list[dict[str, Any]] = []
        for s_info in c_info["sections"].values():
            topics_list = list(s_info["topics"].values())
            sections_list.append(
                {
                    "id": s_info["id"],
                    "title": s_info["title"],
                    "summary": s_info["summary"],
                    "topics": topics_list,
                }
            )
        formatted_chapters.append(
            {
                "id": c_info["id"],
                "title": c_info["title"],
                "chapter_number": c_info["chapter_number"],
                "sections": sections_list,
            }
        )

    return {
        "document_id": document_id,
        "chapters": formatted_chapters,
        "nodes": list(nodes.values()),
        "edges": edges,
    }


def get_learning_path(document_id: str) -> list[dict[str, Any]]:
    """
    Generate an ordered learning path of topics and subtopics with prerequisite gates.
    """
    steps: list[dict[str, Any]] = []
    step_idx = 1
    prior_topic_names: list[str] = []

    try:
        driver = get_neo4j_driver()
        cypher = """
        MATCH (c:Chapter {document_id: $doc_id})
        OPTIONAL MATCH (c)-[:CONTAINS_SECTION]->(s:Section {document_id: $doc_id})
        OPTIONAL MATCH (s)-[:CONTAINS_TOPIC]->(t:Topic {document_id: $doc_id})
        OPTIONAL MATCH (t)-[:CONTAINS_SUBTOPIC]->(st:Subtopic {document_id: $doc_id})
        RETURN c, s, t, st
        ORDER BY c.chapter_number, c.title, s.title, t.name, st.name
        """
        seen_topics: set[str] = set()
        last_section_id: str | None = None

        with driver.session() as session:
            res = session.run(cypher, doc_id=document_id)
            for record in res:
                s = record["s"]
                t = record["t"]
                st = record["st"]

                if t and t["id"] not in seen_topics:
                    seen_topics.add(t["id"])
                    # Sibling topics under the same section can be studied interchangeably
                    curr_section_id = s["id"] if s else None
                    is_interchangeable = bool(
                        curr_section_id and curr_section_id == last_section_id
                    )
                    last_section_id = curr_section_id

                    steps.append(
                        {
                            "step_index": step_idx,
                            "id": t["id"],
                            "name": t.get("name", t["id"]),
                            "type": "TOPIC",
                            "summary": t.get("summary", ""),
                            "needs_context": False,
                            "prerequisites": list(prior_topic_names[-2:]),  # Immediate prerequisites
                            "is_interchangeable": is_interchangeable,
                        }
                    )
                    prior_topic_names.append(t.get("name", t["id"]))
                    step_idx += 1

                if st:
                    steps.append(
                        {
                            "step_index": step_idx,
                            "id": st["id"],
                            "name": st.get("name", st["id"]),
                            "type": "SUBTOPIC",
                            "summary": st.get("summary", ""),
                            "needs_context": st.get("needs_context", False),
                            "prerequisites": [t.get("name", t["id"])] if t else [],
                            "is_interchangeable": False,
                        }
                    )
                    step_idx += 1

    except (Neo4jError, ServiceUnavailable, OSError) as exc:
        logger.warning("Neo4j learning path fetch error: %s", exc)

    return steps


def get_node_dossier(document_id: str, node_id: str) -> dict[str, Any]:
    """
    Retrieve comprehensive dossier for an entity or concept:
    attributes, incoming/outgoing relationships, and verbatim chunks.
    """
    node_info: dict[str, Any] = {
        "node_id": node_id,
        "name": node_id,
        "type": "CONCEPT",
        "description": "",
    }
    incoming_relations: list[dict[str, Any]] = []
    outgoing_relations: list[dict[str, Any]] = []
    text_chunks: list[dict[str, Any]] = []

    try:
        driver = get_neo4j_driver()
        with driver.session() as session:
            # 1. Fetch node metadata
            node_res = session.run(
                """
                MATCH (n {id: $node_id, document_id: $doc_id})
                RETURN n
                LIMIT 1
                """,
                node_id=node_id,
                doc_id=document_id,
            ).single()

            if node_res and node_res["n"]:
                n = node_res["n"]
                node_info["name"] = n.get("name", n.get("title", node_id))
                node_info["type"] = n.get("type", "CONCEPT")
                node_info["description"] = n.get(
                    "description", n.get("summary", "")
                )

            # 2. Fetch outgoing relations
            out_res = session.run(
                """
                MATCH (n {id: $node_id, document_id: $doc_id})-[r]->(m {document_id: $doc_id})
                RETURN r, m
                LIMIT 20
                """,
                node_id=node_id,
                doc_id=document_id,
            )
            for rec in out_res:
                r = rec["r"]
                m = rec["m"]
                outgoing_relations.append(
                    {
                        "source": node_id,
                        "target": m["id"],
                        "relation": r.type if hasattr(r, "type") else r.get("relation", "CONNECTED_TO"),
                        "description": r.get("description", ""),
                        "weight": r.get("weight", 1.0),
                    }
                )

            # 3. Fetch incoming relations
            in_res = session.run(
                """
                MATCH (m {document_id: $doc_id})-[r]->(n {id: $node_id, document_id: $doc_id})
                RETURN m, r
                LIMIT 20
                """,
                node_id=node_id,
                doc_id=document_id,
            )
            for rec in in_res:
                r = rec["r"]
                m = rec["m"]
                incoming_relations.append(
                    {
                        "source": m["id"],
                        "target": node_id,
                        "relation": r.type if hasattr(r, "type") else r.get("relation", "CONNECTED_TO"),
                        "description": r.get("description", ""),
                        "weight": r.get("weight", 1.0),
                    }
                )

    except (Neo4jError, ServiceUnavailable, OSError) as exc:
        logger.warning("Neo4j dossier fetch error for node %s: %s", node_id, exc)

    # 4. Search verbatim chunks mentioning or semantically close to node
    try:
        embedding_service = get_embedding_service()
        query_vector = embedding_service.embed_query(node_id)
        qdrant = get_qdrant_client()
        doc_filter = Filter(
            must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]
        )
        hits = qdrant.query_points(
            collection_name=CHUNKS_COLLECTION,
            query=query_vector,
            query_filter=doc_filter,
            limit=4,
        ).points

        for h in hits:
            if h.payload:
                text_chunks.append(
                    {
                        "chunk_index": h.payload.get("chunk_index"),
                        "page_number": h.payload.get("page_number"),
                        "text": h.payload.get("text", ""),
                        "score": h.score,
                    }
                )
    except (ApiException, OSError, RuntimeError, ValueError) as exc:
        logger.warning("Qdrant dossier chunk fetch error: %s", exc)

    return {
        "node_id": node_info["node_id"],
        "name": node_info["name"],
        "type": node_info["type"],
        "description": node_info["description"],
        "incoming_relations": incoming_relations,
        "outgoing_relations": outgoing_relations,
        "text_chunks": text_chunks,
    }


def get_communities_list(document_id: str) -> list[dict[str, Any]]:
    """
    List all community clusters with summaries, ratings, and member entities.
    """
    communities: list[dict[str, Any]] = []

    try:
        driver = get_neo4j_driver()
        cypher = """
        MATCH (c:Community {document_id: $doc_id})
        OPTIONAL MATCH (c)-[:INCLUDES_ENTITY]->(e:Entity {document_id: $doc_id})
        RETURN c.id AS id, c.title AS title, c.summary AS summary,
               c.key_findings AS key_findings, c.rating AS rating,
               collect(e.id) AS member_ids
        ORDER BY c.rating DESC
        """
        with driver.session() as session:
            result = session.run(cypher, doc_id=document_id)
            for rec in result:
                member_ids = rec["member_ids"] or []
                communities.append(
                    {
                        "id": rec["id"],
                        "title": rec["title"] or f"Community {rec['id']}",
                        "summary": rec["summary"] or "",
                        "key_findings": rec["key_findings"] or [],
                        "rating": rec["rating"] or 8.0,
                        "member_ids": member_ids,
                        "member_count": len(member_ids),
                    }
                )
    except (Neo4jError, ServiceUnavailable, OSError) as exc:
        logger.warning("Neo4j community list fetch error: %s", exc)

    return communities


def generate_exam_gist(document_id: str) -> dict[str, Any]:
    """
    Synthesize a 2-minute high-yield exam revision guide.
    """
    concepts: list[dict[str, str]] = []

    try:
        driver = get_neo4j_driver()
        cypher = """
        MATCH (t:Topic {document_id: $doc_id})
        RETURN t.name AS name, t.summary AS summary
        UNION
        MATCH (e:Entity {document_id: $doc_id})
        RETURN e.name AS name, e.description AS summary
        LIMIT 25
        """
        with driver.session() as session:
            result = session.run(cypher, doc_id=document_id)
            for rec in result:
                if rec["name"]:
                    concepts.append(
                        {
                            "name": rec["name"],
                            "summary": rec["summary"] or "",
                        }
                    )
    except (Neo4jError, ServiceUnavailable, OSError) as exc:
        logger.warning("Neo4j exam gist concepts fetch error: %s", exc)

    if not concepts:
        return {
            "document_id": document_id,
            "top_concepts": [],
            "key_formulas": [],
            "common_pitfalls": [],
            "likely_questions": [],
        }

    concepts_text = "\n".join(f"- {c['name']}: {c['summary']}" for c in concepts)

    try:
        model = get_synthesis_model().with_structured_output(ExamGistResult)
        prompt = EXAM_GIST_PROMPT.invoke({"text": concepts_text})
        gist_res: ExamGistResult = model.invoke(prompt)
        return {
            "document_id": document_id,
            "top_concepts": gist_res.top_concepts,
            "key_formulas": gist_res.key_formulas,
            "common_pitfalls": gist_res.common_pitfalls,
            "likely_questions": gist_res.likely_questions,
        }
    except (ValueError, RuntimeError, OSError) as exc:
        logger.warning("Exam gist LLM synthesis fallback: %s", exc)
        return {
            "document_id": document_id,
            "top_concepts": [c["name"] for c in concepts[:5]],
            "key_formulas": ["Review foundational definitions and theorems."],
            "common_pitfalls": ["Overlooking edge cases and prerequisite assumptions."],
            "likely_questions": [f"Explain the primary role of {concepts[0]['name']}."],
        }

