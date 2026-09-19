# AI GraphRAG Backend Implementation Plan

Untangle's AI GraphRAG backend is responsible for ingesting academic literature (Research Mode) and textbooks (Study Mode), transforming unstructured texts into a typed knowledge graph and vector index, and powering hybrid retrieval (local entity expansion + global community summarization) through Regulus, an AI guide that streams citations and lights up the knowledge map.

---

## Architecture Overview

```
                         [Client (Vue 3 / Vite)]
                                   │
              REST APIs            │          WebSocket
           (/documents, /graph)    │     (/ws/chat, /ws/progress)
                                   ▼
                   ┌───────────────────────────────┐
                   │     FastAPI Backend Core      │
                   │   Auth: Clerk JWT (deps.py)   │
                   └───────────────┬───────────────┘
                                   │
           ┌───────────────────────┼───────────────────────┐
           ▼                       ▼                       ▼
    [Relational DB]         [Graph DB]              [Vector DB]
      PostgreSQL /           Neo4j 5.x               Qdrant
        SQLite             (:Entity, :Topic,       (Chunks & Entities
   (Users, Documents,       :Community, :Road)       Dense Vectors)
     Jobs, Sessions)               ▲                       ▲
                                   │                       │
                                   └───────────┬───────────┘
                                               │
                   ┌───────────────────────────┴───┐
                   │    Async Ingestion Engine     │
                   │      (Celery + Redis)         │
                   └───────────────┬───────────────┘
                                   │
          ┌────────────────────────┴────────────────────────┐
          ▼                                                 ▼
[Research Mode Pipeline]                          [Study Mode Pipeline]
• PDF/Text Chunking (~600 toks)                  • Structural TOC / Chapter parse
• Gemini 2.5 Flash-Lite NER Extraction           • Topic & Subtopic hierarchy
• 3-Tier Entity Deduplication                    • CONCEPTUALLY_LINKS & NEEDS_CONTEXT
• Leiden Community Detection                     • Cross-Source Auto-Suggestions
• Community Summarization                        • High-Yield Exam Gist Gen
                                   │
                                   ▼
                   ┌───────────────────────────────┐
                   │     Hybrid Retrieval Engine   │
                   │ (Local Search + Global Search)│
                   └───────────────┬───────────────┘
                                   │
                                   ▼
                   ┌───────────────────────────────┐
                   │   Regulus AI Guide Streamer   │
                   │  Groq Llama 3.3 70B (<150ms)  │
                   │   Emits: Tokens + Subgraph    │
                   └───────────────────────────────┘
```

---

## Infrastructure & Model Configuration

* **Extraction / Ingestion Workhorse**: **Google Gemini 2.5 Flash-Lite** (`gemini-2.5-flash-lite`) via Google AI Studio API for free 1,500 RPD, 30 RPM, and 1M token context.
* **Textbook Hierarchy & Summarization**: **Google Gemini 2.5 Flash** (`gemini-2.5-flash`) for structural extraction, community summaries, and high-yield exam gists.
* **Real-Time Interactive Chat**: **Groq Cloud** (`llama-3.3-70b-versatile`) for `<150ms` streaming generation, strictly reserved for chat to stay within Groq's 100,000 Tokens-Per-Day organization quota.
* **Dense Vector Embeddings**: Local **`fastembed` (BAAI/bge-small-en-v1.5)** running on CPU (384 dimensions, zero external API costs, ~10ms per batch).
* **Storage Stack**:
  * Relational: PostgreSQL (with SQLite local file fallback `untangle.db` for rapid local dev).
  * Graph: Neo4j 5.x (with Cypher query builder and NetworkX in-memory mock for dev testing).
  * Vector: Qdrant (local file/memory mode or containerized).
  * Broker: Redis (with in-process task runner fallback).

---

## Proposed Modules & Implementation Roadmap

### 1. Database Schemas & Storage Layer

Expand the database models from just `users` to include document metadata, asynchronous processing jobs, cross-source link records, and chat history.

#### [backend/app/core/config.py](file:///f:/Subhraneel/BIG%20PROJECTS/Untangle/backend/app/core/config.py)
* Add typed settings for:
  * `GEMINI_API_KEY`, `EXTRACTION_MODEL` (`gemini-2.5-flash-lite`), `SYNTHESIS_MODEL` (`gemini-2.5-flash`).
  * `GROQ_API_KEY`, `GROQ_CHAT_MODEL` (`llama-3.3-70b-versatile`).
  * `EMBEDDING_PROVIDER` (`fastembed`), `EMBEDDING_MODEL` (`BAAI/bge-small-en-v1.5`).
  * `UPLOAD_DIR` (local storage for uploaded PDF/EPUB/TXT files).

#### [backend/app/models/document.py](file:///f:/Subhraneel/BIG%20PROJECTS/Untangle/backend/app/models/document.py)
* `Document`: `id`, `user_id`, `filename`, `file_path`, `file_size`, `source_mode` (`research` | `study`), `display_title`, `status` (`pending` | `parsing` | `chunking` | `extracting` | `deduping` | `clustering` | `summarizing` | `ready` | `failed`), `error_message`, `stats` (`chunk_count`, `entity_count`, `community_count`, `chapter_count`).
* `DocumentLink`: `id`, `source_document_id`, `target_document_id`, `topic_id`, `link_reason`, `link_mode` (`auto` | `manual`), `status` (`suggested` | `accepted` | `rejected`).
* `IngestionJob`: tracks task ID, current step, percent completion, and message logs.

#### [backend/app/models/chat.py](file:///f:/Subhraneel/BIG%20PROJECTS/Untangle/backend/app/models/chat.py)
* `ChatSession`: `id`, `user_id`, `document_id`, `title`, `search_mode` (`local` | `global` | `auto`), `created_at`.
* `ChatMessage`: `id`, `session_id`, `role` (`user` | `assistant`), `content`, `retrieved_subgraph` (JSON: `{node_ids: [...], edge_ids: [...]}`), `citations` (JSON: list of chunk IDs and text snippets), `latency_ms`.

#### [backend/app/db/neo4j.py](file:///f:/Subhraneel/BIG%20PROJECTS/Untangle/backend/app/db/neo4j.py)
* Neo4j driver connection manager and session context manager (`get_neo4j_session`).
* Schema constraint and index initializers:
  * Constraints: unique `(:Entity {id, document_id})`, unique `(:Topic {id, document_id})`, unique `(:Chunk {id, document_id})`, unique `(:Community {id, document_id})`.
  * Indexes on `Entity.name`, `Topic.name`, `Chunk.index`.

#### [backend/app/db/qdrant.py](file:///f:/Subhraneel/BIG%20PROJECTS/Untangle/backend/app/db/qdrant.py)
* Qdrant client singleton and collection initialization:
  * `chunks` collection (vector dimension: 384 for `bge-small-en-v1.5`, cosine metric, payload indexed on `document_id`).
  * `entities` collection (384 dims, payload: `name`, `type`, `document_id`).
  * `topics` collection (384 dims, payload: `name`, `document_id`, `needs_context`).

---

### 2. LLM Client & Prompt Engine (`app/llm/`)

Unified, swappable model provider with strict Pydantic JSON schema output validation and rate-limit retry handling.

#### [backend/app/llm/client.py](file:///f:/Subhraneel/BIG%20PROJECTS/Untangle/backend/app/llm/client.py)
* Universal LLM interface with support for:
  * **Google Gemini Client** (`google-genai` / HTTP SDK) with native `response_mime_type="application/json"` and Pydantic schemas.
  * **Groq Client** (`openai.AsyncOpenAI(base_url="https://api.groq.com/openai/v1")`) with streaming support for low-latency Regulus chat.
  * **Fallback / OpenAI-compatible router** (DeepSeek, Hugging Face router, Ollama).
* Built-in exponential backoff retry handler (`tenacity`) targeting `429 Too Many Requests` and `503 Service Unavailable`.

#### [backend/app/llm/embeddings.py](file:///f:/Subhraneel/BIG%20PROJECTS/Untangle/backend/app/llm/embeddings.py)
* Embedding service using `fastembed` (running ONNX-optimized `BAAI/bge-small-en-v1.5` on CPU, 384 dimensions, zero external API costs, ~10ms per batch).
* Fallback to sentence-transformers or OpenAI embedding API if configured.

#### [backend/app/llm/prompts.py](file:///f:/Subhraneel/BIG%20PROJECTS/Untangle/backend/app/llm/prompts.py)
* **Extraction Prompt (Research Mode)**: Few-shot extraction of nodes `(name, type: PERSON|ORG|CONCEPT|LOCATION, description)` and edges `(source, target, relation, description)` with strict schema validation.
* **Structural Hierarchy Prompt (Study Mode)**: Extract `Chapter -> Section -> Topic -> Subtopic` with parent references and 2-sentence summaries.
* **Concept Dependency & Scope Prompt (Study Mode)**: Detect `CONCEPTUALLY_LINKS` relationships and `needs_context=True` prerequisites.
* **Community Summary Prompt**: Leiden cluster thematic synthesis (`title`, `summary`, `key_findings`, `weight_rating`).
* **High-Yield Exam Gist Prompt**: Identify top essential exam concepts, formulas to memorize, common conceptual traps, and potential test questions.
* **Regulus Synthesis Prompt**: Multi-hop grounded reasoning, citing exact chunk numbers `[Chunk X]`.

---

### 3. Ingestion & Processing Pipeline (`app/services/ingestion/` & `app/tasks/`)

Handle document parsing, text chunking, graph population, community detection, and vector indexing.

#### [backend/app/services/parser.py](file:///f:/Subhraneel/BIG%20PROJECTS/Untangle/backend/app/services/parser.py)
* Document text extractor supporting PDF (`pypdf` / `unstructured`), TXT, and Markdown.
* Sentence-aware text chunker:
  * Target: ~500–600 tokens per chunk (~2,000 characters).
  * Overlap: ~15% (~75–100 tokens) to maintain contextual coherence across chunk boundaries.
  * Metadata preservation: `chunk_index`, `page_number`, `token_count`.

#### [backend/app/services/graph_service.py](file:///f:/Subhraneel/BIG%20PROJECTS/Untangle/backend/app/services/graph_service.py)
* Cypher execution helpers:
  * Batch `MERGE` entities and relationships into Neo4j.
  * Structural hierarchy tree insertion for Study Mode.
  * 3-tier entity deduplication:
    1. Case-insensitive exact name match.
    2. Embedding cosine similarity threshold ($\ge 0.88$) in Qdrant.
    3. LLM disambiguation for borderline cases ($0.75 \le \text{similarity} < 0.88$), executing `apoc.refactor.mergeNodes`.
* Community detection algorithm:
  * Calls Neo4j GDS Leiden / Louvain algorithm (or Python `networkx` / `cdlib` fallback if GDS is not installed in the container).
  * Creates `(:Community)` nodes and `[:BELONGS_TO]` edges.

#### [backend/app/tasks/ingestion.py](file:///f:/Subhraneel/BIG%20PROJECTS/Untangle/backend/app/tasks/ingestion.py)
* Async task pipeline:
  * `task_parse_and_chunk(doc_id)`
  * `task_extract_entities_or_hierarchy(doc_id, mode)`
  * `task_deduplicate_and_embed(doc_id)`
  * `task_cluster_and_summarize(doc_id)`
  * Publishes progress events to Redis channel `progress:{document_id}` (`{step, progress, detail, towersBuilt, roadsLaid}`).

---

### 4. Hybrid Retrieval & Search Services (`app/services/search/`)

The core GraphRAG retrieval logic combining local subgraph expansion and global community map-reduce.

#### [backend/app/services/retrieval/local_search.py](file:///f:/Subhraneel/BIG%20PROJECTS/Untangle/backend/app/services/retrieval/local_search.py)
* **Seed Entity Discovery**: Embed user query with `bge-small-en-v1.5`, search Qdrant `entities` collection for top-5 closest entities.
* **Subgraph Expansion**: Run 1-hop and 2-hop Cypher traversal in Neo4j from seed entities:
  * Collect connected entities, relationship descriptions, and connected chunks.
* **Context Assembly & Reranking**: Sort chunks by cosine similarity to the question; build a structured prompt context containing:
  * Entities & their descriptions
  * Relationships & their explanations
  * Top verbatim chunks
* **Output**: Returns answer prompt context + the exact `retrieved_subgraph` (`{node_ids, edge_ids}`) for frontend illumination.

#### [backend/app/services/retrieval/global_search.py](file:///f:/Subhraneel/BIG%20PROJECTS/Untangle/backend/app/services/retrieval/global_search.py)
* **Community-level Map-Reduce**:
  * For broad/thematic queries ("What are the main architectural innovations?"):
  * Fetch all hierarchical Community summaries from Neo4j.
  * **Map Stage**: LLM evaluates each community summary for relevance and extracts point answers with relevance rating (0–100).
  * **Reduce Stage**: Filter out low-relevance communities, sort by rating, and synthesize a coherent, high-level answer with citations to communities and source papers.

#### [backend/app/services/retrieval/study_features.py](file:///f:/Subhraneel/BIG%20PROJECTS/Untangle/backend/app/services/retrieval/study_features.py)
* **Learning Path Generator**: Topological dependency ordering of concepts using Cypher path traversal (`CONCEPTUALLY_LINKS`).
* **Topic Dossier Builder**: Assembles exhaustive reference material for any clicked tower (all verbatim chunks, formulas, connected concepts, outside prerequisites).
* **High-Yield Exam Gist Generator**: Precomputes or serves the top high-yield exam takeaways for quick review.

---

### 5. API Endpoints & Real-time WebSockets (`app/api/v1/endpoints/`)

Expose clean REST and streaming WebSocket interfaces matching the frontend contracts.

#### [backend/app/api/v1/endpoints/documents.py](file:///f:/Subhraneel/BIG%20PROJECTS/Untangle/backend/app/api/v1/endpoints/documents.py)
* `POST /documents/upload`: Multipart upload with `source_mode` parameter, file validation, storage, and pipeline trigger.
* `GET /documents`: List user's documents with status, realm stats, and mode.
* `GET /documents/{id}`: Detailed document status.
* `DELETE /documents/{id}`: Cascade deletes document, Qdrant vectors, and Neo4j graph nodes.
* `GET /documents/{id}/exam-gist`: Returns the high-yield exam summary for fast revision.
* `GET /documents/{id}/suggest-sources`: Surfaces auto-suggested external sources for `NEEDS_CONTEXT` topics.
* `POST /documents/{id}/link-source`: Links external papers/books.

#### [backend/app/api/v1/endpoints/graph.py](file:///f:/Subhraneel/BIG%20PROJECTS/Untangle/backend/app/api/v1/endpoints/graph.py)
* `GET /graph/{document_id}/town` *(Research Mode)*: Returns buildings (entities with type, level, mention count) and roads (relationships).
* `GET /graph/{document_id}/study-map` *(Study Mode)*: Returns chapter districts, topic/subtopic towers, and conceptual links.
* `GET /graph/{document_id}/communities`: Returns community clusters with summaries and member IDs.
* `GET /graph/{document_id}/learning-path`: Returns the ordered step-by-step curriculum sequence.
* `GET /graph/{document_id}/nodes/{node_id}/dossier`: Returns the complete chunk/formula reading dossier for a node.

#### [backend/app/api/v1/endpoints/chat.py](file:///f:/Subhraneel/BIG%20PROJECTS/Untangle/backend/app/api/v1/endpoints/chat.py)
* `POST /chat/sessions`: Create a new chat session for a document.
* `GET /chat/sessions/{session_id}/messages`: Retrieve conversation history.
* `POST /chat/sessions/{session_id}/messages`: Synchronous chat endpoint (for testing/eval).

#### [backend/app/api/v1/endpoints/ws.py](file:///f:/Subhraneel/BIG%20PROJECTS/Untangle/backend/app/api/v1/endpoints/ws.py)
* `WebSocket /ws/documents/{document_id}/progress`: Real-time ingestion telemetry (streams parse, chunk, extract, cluster progress).
* `WebSocket /ws/chat/{session_id}`: Interactive Regulus streaming chat:
  * Streams answer tokens live via Groq 70B (`{"type": "token", "content": "..."}`).
  * Emits the final payload with citations and the highlighted subgraph:
    ```json
    {
      "type": "done",
      "citations": [{"chunk_id": "...", "text": "..."}],
      "subgraph": {
        "node_ids": ["entity_1", "entity_4"],
        "edge_ids": ["rel_1_4"]
      },
      "search_mode": "local",
      "latency_ms": 340
    }
    ```

---

### 6. Router & Main Wiring

#### [backend/app/api/v1/router.py](file:///f:/Subhraneel/BIG%20PROJECTS/Untangle/backend/app/api/v1/router.py)
* Register `documents`, `graph`, `chat`, and `ws` routers alongside existing `auth` router.

#### [backend/app/main.py](file:///f:/Subhraneel/BIG%20PROJECTS/Untangle/backend/app/main.py)
* Register database table initialization on startup (`Base.metadata.create_all`).
* Wire CORS and WebSocket routes.

---

## Verification Plan

### Automated Tests
Run via pytest in `backend/`:
```powershell
uv run pytest tests/ -v
```
Test suite will include:
1. `tests/test_parser.py`: Unit tests for PDF/TXT text extraction and sliding-window chunking.
2. `tests/test_embeddings.py`: Fastembed local model verification (dimension check = 384, vector norm check).
3. `tests/test_llm_schemas.py`: Schema validation testing for Entity Extraction and Study Mode Hierarchy extraction JSON parsing.
4. `tests/test_retrieval.py`: Local search context assembly and subgraph payload structure verification using mock data.
5. `tests/test_api_documents.py`: Document upload, list, and metadata endpoints.

### Manual End-to-End Verification
1. **Upload & Ingestion Progress**:
   * Upload a sample paper (e.g. *Attention Is All You Need* PDF).
   * Observe WebSocket progression: `parse` $\rightarrow$ `chunk` $\rightarrow$ `extract` $\rightarrow$ `cluster` $\rightarrow$ `ready`.
2. **Graph Visual Verification**:
   * Call `GET /api/v1/graph/{id}/town` and verify building positions and road links.
3. **Regulus Streaming & Subgraph Illumination**:
   * Connect to `/ws/chat/{session_id}`.
   * Send question: *"How does Scaled Dot-Product Attention prevent vanishing gradients?"*
   * Verify token streaming begins in `<200ms`.
   * Verify the `done` event includes `subgraph.node_ids` and `citations` matching the relevant concepts.
4. **Study Mode Hierarchy**:
   * Upload a textbook chapter, select **Study Mode**.
   * Call `GET /api/v1/graph/{id}/study-map` and verify chapter $\rightarrow$ section $\rightarrow$ topic nesting and `needs_context` flags.

