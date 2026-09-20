# Untangle Backend — Full Build Plan

> **Phase 0 Decisions (Resolved)**
> 1. **Primary model**: Gemini 3.5 Flash-Lite → Fallback: Gemini 2.5 Flash-Lite
> 2. **Cost tolerance**: $0 — free tier only, rate-limit retries acceptable
> 3. **Task queue**: Redis + Celery (no in-process fallback)

---

## API Rate Limit Audit

The [ai_rag_backend_implementation_plan.md](./ai_rag_backend_implementation_plan.md) contains **several inaccurate free-tier rate limit claims**:

### What the Plan Claims vs. Actual Limits

| Provider / Model | Plan Claims | Actual Free Tier (Sept 2026) | Verdict |
|---|---|---|---|
| **Gemini 2.5 Flash-Lite** (Extraction) | "1,500 RPD, 30 RPM, 1M context" | ~5–10 RPM, ~100–250 RPD (per-project, check AI Studio). Context window = 1M tokens ✅ | ⚠️ RPD/RPM **wildly overstated** |
| **Gemini 2.5 Flash** (Synthesis) | Not explicitly limited in plan | ~10 RPM, ~250 RPD, 250K TPM | ⚠️ Usable but tight for batch ingestion |
| **Groq `llama-3.3-70b-versatile`** (Chat) | "100,000 Tokens-Per-Day org quota" | **30 RPM, 1K RPD, 8K TPM, 200K TPD** | ⚠️ 8K TPM is the real bottleneck |
| **fastembed `bge-small-en-v1.5`** (Embeddings) | "Zero cost, ~10ms/batch, 384 dims" | ✅ Accurate — runs locally on CPU | ✅ Correct |

> **Note:** Gemini 2.5 Flash is scheduled for retirement on October 16, 2026. By using LangChain's `init_chat_model()`, swapping to 3.x models is a one-line config change.

---

## Corrected Multi-Provider LLM Strategy

| Role | Primary Model | Fallback Model | Rationale |
|---|---|---|---|
| **Extraction / NER** (batch) | Gemini 3.5 Flash-Lite | Gemini 2.5 Flash-Lite | Flash-Lite gets highest RPD; 10M context window tokens |
| **Synthesis / Summaries** (batch) | Gemini 3.5 Flash | Groq `llama-3.3-70b` | Community summaries are batch — can retry on 429 |
| **Real-time Chat (Regulus)** | Groq `llama-3.3-70b-versatile` | Gemini 3.5 Flash (streaming) | Groq LPU gives <150ms TTFT; Gemini as backup |
| **Embeddings** | Local `fastembed` (`bge-small-en-v1.5`) | — | Zero API cost, 384 dims, ~10ms/batch |

---

## Architecture: LangGraph + LangChain

```
┌─────────────────────────────────────────────┐
│         app/llm/client.py                    │
│                                              │
│  init_chat_model(settings.EXTRACTION_MODEL,  │
│                  model_provider="google-genai")│
│                                              │
│  init_chat_model(settings.CHAT_MODEL,        │
│                  model_provider="groq")       │
│                                              │
│  → Returns BaseChatModel                     │
│  → .invoke() / .stream() / .bind_tools()     │
│  → Swap model by changing .env config        │
└─────────────────────────────────────────────┘
                    │
          ┌─────────┴──────────┐
          ▼                    ▼
   LangGraph Agent       LangGraph Agent
   (Ingestion Pipeline)  (Regulus Chat)
   ┌──────────────┐      ┌──────────────┐
   │ parse        │      │ classify     │
   │ chunk        │      │ retrieve     │
   │ extract      │      │ synthesize   │
   │ deduplicate  │      │ stream       │
   │ embed        │      └──────────────┘
   │ cluster      │
   │ summarize    │
   └──────────────┘
```

**Key benefit**: Swap any model by changing one `.env` variable:
```env
CHAT_MODEL=gpt-4o
CHAT_MODEL_PROVIDER=openai
```
No code changes required.

---

## Build Roadmap (Feature-by-Feature)

Each feature is built, tested, and verified before moving to the next.

### Feature 1: Database Models & Storage Layer

**Files to create/modify:**
- `app/models/document.py` — Document, DocumentLink, IngestionJob models
- `app/models/chat.py` — ChatSession, ChatMessage models
- `app/schemas/document.py` — Pydantic schemas for documents
- `app/schemas/chat.py` — Pydantic schemas for chat
- `app/db/base.py` — Register new models
- `app/core/config.py` — Add new settings (Gemini keys, Groq keys, embedding config, upload dir)
- `app/db/neo4j.py` — Neo4j driver connection manager
- `app/db/qdrant.py` — Qdrant client singleton
- `tests/test_models.py` — SQLite-based model CRUD tests

**Test gate:** `uv run pytest tests/test_models.py` — all pass

---

### Feature 2: LLM Client Layer (LangChain/LangGraph)

**Files to create:**
- `app/llm/client.py` — Model-agnostic LLM interface using `langchain.chat_models.init_chat_model()`:
  - `get_extraction_model()` → Gemini 3.5 Flash-Lite (fallback: 2.5 Flash-Lite)
  - `get_synthesis_model()` → Gemini 3.5 Flash
  - `get_chat_model()` → Groq `llama-3.3-70b-versatile`
  - Built-in `tenacity` retry with exponential backoff on 429/503
- `app/llm/embeddings.py` — `fastembed` wrapper (`bge-small-en-v1.5`, 384 dims)
- `app/llm/prompts.py` — All prompt templates as LangChain `ChatPromptTemplate` objects
- `tests/test_llm_client.py` — Unit tests with mock models
- `tests/test_embeddings.py` — Verify fastembed loads, produces 384-dim vectors

**New dependencies:**
```
langchain-core, langchain-google-genai, langchain-groq, langgraph, fastembed, tenacity
```

**Test gate:** `uv run pytest tests/test_llm_client.py tests/test_embeddings.py` — all pass

---

### Feature 3: Document Parser & Chunker

**Files to create:**
- `app/services/parser.py` — PDF/TXT/Markdown text extraction (pypdf), sentence-aware chunker (~500-600 tokens, 15% overlap)
- `tests/test_parser.py` — Unit tests with sample text files

**Test gate:** `uv run pytest tests/test_parser.py` — all pass

---

### Feature 4: Document Upload & Management API

**Files to create/modify:**
- `app/api/v1/endpoints/documents.py` — `POST /documents/upload`, `GET /documents`, `GET /documents/{id}`, `DELETE /documents/{id}`
- `app/services/document_service.py` — Business logic for document CRUD
- `app/api/v1/router.py` — Mount documents router
- `tests/test_api_documents.py` — Upload, list, delete tests

**Test gate:** `uv run pytest tests/test_api_documents.py` — all pass

---

### Feature 5: Ingestion Pipeline (Celery + LangGraph)

**Files to create:**
- `app/services/ingestion/pipeline.py` — LangGraph state machine:
  ```
  parse → chunk → extract_entities → deduplicate → embed → cluster → summarize → done
  ```
- `app/services/ingestion/extractors.py` — Entity/hierarchy extraction using LLM client
- `app/services/graph_service.py` — Neo4j Cypher execution helpers
- `app/tasks/ingestion.py` — Celery task definitions
- `app/tasks/celery_app.py` — Celery application factory (Redis broker)
- `tests/test_ingestion.py` — Pipeline tests with mock LLM responses

**Test gate:** `uv run pytest tests/test_ingestion.py` — all pass

---

### Feature 6: Graph API & Retrieval

**Files to create:**
- `app/api/v1/endpoints/graph.py` — `GET /graph/{doc_id}/town`, `/study-map`, `/communities`, `/learning-path`, `/nodes/{id}/dossier`
- `app/services/retrieval/local_search.py` — Seed entity discovery + subgraph expansion
- `app/services/retrieval/global_search.py` — Community map-reduce
- `app/services/retrieval/study_features.py` — Learning path, topic dossier, exam gist
- `tests/test_retrieval.py` — Retrieval tests with mock Neo4j/Qdrant data

**Test gate:** `uv run pytest tests/test_retrieval.py` — all pass

---

### Feature 7: Chat & WebSocket Streaming

**Files to create:**
- `app/api/v1/endpoints/chat.py` — `POST /chat/sessions`, `GET /chat/sessions/{id}/messages`
- `app/api/v1/endpoints/ws.py` — `WebSocket /ws/chat/{session_id}`, `WebSocket /ws/documents/{doc_id}/progress`
- `app/services/chat_service.py` — LangGraph-powered Regulus agent
- `app/tasks/celery_app.py` — Redis pub/sub for progress events
- `tests/test_chat.py` — Chat endpoint tests
- `tests/test_ws.py` — WebSocket streaming tests

**Test gate:** `uv run pytest tests/test_chat.py tests/test_ws.py` — all pass

---

## Verification Plan

### Per-Feature Automated Tests
```powershell
uv run pytest tests/ -v
```

### End-to-End Manual Verification

After Feature 5:
1. Upload a sample PDF → observe Celery worker ingestion + Redis progress events
2. Call `GET /api/v1/graph/{id}/town` → verify entity/relationship data

After Feature 7:
3. Connect to WebSocket → send question → verify streaming + subgraph illumination
4. Verify Groq streaming latency < 200ms TTFT

