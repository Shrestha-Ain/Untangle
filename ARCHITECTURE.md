# Untangle — Complete System Architecture & Codebase Gist

> **Living Documentation**: This document serves as the comprehensive architectural and implementation blueprint for **Untangle**. Whenever code changes, new endpoints, state variables, or database schemas are modified or added, this document should be updated accordingly.

---

## 1. Executive Overview & Product Vision

**Untangle** is an isometric, game-like **GraphRAG (Graph-Augmented Retrieval-Augmented Generation) Knowledge Mapping Platform**. It converts dense academic literature (research papers) and textbooks into explorable cartographic "towns" and "realms".

### Core Capabilities
1. **Research Mode**:
   - Ingests academic literature (PDF/TXT).
   - Extracts semantic entities (Concepts, Methods, Datasets, Authors) and typed relationships.
   - Detects thematic community clusters.
   - Generates isometric maps where entities are buildings/towers, relationships are roads/bridges, and communities form districts.
2. **Study Mode**:
   - Ingests textbooks and syllabi.
   - Parses hierarchical structures: Chapters &rarr; Sections &rarr; Topics.
   - Derives sequential **Learning Paths** (prerequisite topic progression).
   - Generates **Exam Gists** (high-yield revision sheets, formulas to memorize, exam traps).
3. **Regulus (AI Cartographer Guide)**:
   - Grounded GraphRAG conversational assistant.
   - Performs **Hybrid Search** (vector similarity via Qdrant + graph traversal via Neo4j + community summarization).
   - Dynamically **illuminates the graph** in real-time as it answers questions, providing visual citations alongside verbatim chunk sources.

---

## 2. High-Level Architecture Diagram

```mermaid
flowchart TB
    subgraph Client["Frontend Client (Vue 3 + Vite + Tailwind CSS)"]
        UI["User Interface (HomeView / TownExplorerView)"]
        Canvas["Isometric Town Canvas (SVG / Pan-Zoom)"]
        Stores["Pinia Stores (auth, documents, graph, chat, player)"]
        WSClient["WebSocket Client (Ingestion Telemetry & Regulus Chat)"]
        ClerkUI["Clerk Vue SDK (Google OAuth / Email Auth)"]
    end

    subgraph Gateway["API Layer (FastAPI on Port 8000)"]
        AuthMiddleware["Clerk RS256 JWKS JWT Verifier"]
        DocsRouter["/api/v1/documents (Upload, CRUD)"]
        GraphRouter["/api/v1/graph (Town & Dossier APIs)"]
        ChatRouter["/api/v1/chat (Sessions, History)"]
        WSRouter["/ws (Progress Pub/Sub & Token Streaming)"]
    end

    subgraph Async["Background Workers (Celery + Redis)"]
        RedisBroker["Redis 7 (Port 6379) - Broker & Telemetry Pub/Sub"]
        CeleryWorker["Celery Ingestion Worker"]
        LangGraphPipe["LangGraph Ingestion State Machine (7 Nodes)"]
    end

    subgraph Data["Persistence & Knowledge Engines"]
        Postgres[("PostgreSQL 16 (Port 5433)\nUsers, Documents, Jobs, Chats")]
        Neo4j[("Neo4j 5.20 (Bolt 7687)\nEntities, Relationships, Communities")]
        Qdrant[("Qdrant Vector DB (Port 6333)\nDense Semantic Embeddings")]
    end

    subgraph External["External Cloud Services"]
        ClerkCloud["Clerk Identity Provider (JWKS Endpoint)"]
        LLM["LLM Providers (OpenAI GPT-4o / Anthropic Claude / Gemini)"]
    end

    %% Client Connections
    ClerkUI <--> ClerkCloud
    UI --> Stores
    Stores --> Gateway
    WSClient <--> WSRouter
    Canvas <--> Stores

    %% Gateway to Auth
    AuthMiddleware --> ClerkCloud

    %% Gateway to Storage & Workers
    Gateway --> Postgres
    Gateway --> Neo4j
    Gateway --> Qdrant
    Gateway --> RedisBroker

    %% Ingestion Pipeline Flow
    DocsRouter -- "Dispatch Task" --> RedisBroker
    RedisBroker --> CeleryWorker
    CeleryWorker --> LangGraphPipe
    LangGraphPipe --> LLM
    LangGraphPipe --> Postgres
    LangGraphPipe --> Neo4j
    LangGraphPipe --> Qdrant
    LangGraphPipe -- "Pub/Sub Telemetry" --> RedisBroker
    RedisBroker -- "Live Progress" --> WSRouter
```

---

## 3. Storage & Database Matrix

| Store | Tech & Port | Target Data | Key Tables / Collections / Labels |
|---|---|---|---|
| **Relational DB** | PostgreSQL 16 (Port 5433) | Users, documents metadata, cross-document links, ingestion jobs, chat sessions & messages | `users`, `documents`, `document_links`, `ingestion_jobs`, `chat_sessions`, `chat_messages` |
| **Graph DB** | Neo4j 5.20 (Bolt Port 7687) | Structured knowledge graph, topology, hierarchy | Nodes: `:Entity`, `:Community`, `:Chapter`, `:Section`, `:Topic`<br/>Edges: `:RELATED_TO`, `:IN_COMMUNITY`, `:HAS_SECTION`, `:HAS_TOPIC`, `:PREREQUISITE_OF` |
| **Vector DB** | Qdrant (Port 6333) | 384-dim dense vectors (FastEmbed `bge-small-en-v1.5`) | `untangle_chunks` (text chunks + page refs), `untangle_entities` (entity descriptions) |
| **Broker & Cache** | Redis 7 (Port 6379) | Celery message broker & real-time pub/sub channels | Channel: `doc:{doc_id}:progress` |

---

## 4. End-to-End Workflow Lifecycles

### A. Authentication & Just-In-Time (JIT) Provisioning
1. **Frontend Authentication**: User logs in through Clerk (`@clerk/vue`). Clerk produces an RS256 JWT session token.
2. **Token Attachment**: The Axios client (`frontend/src/api/client.ts`) polls `window.Clerk.loaded` and injects `Authorization: Bearer <token>` into outbound requests.
3. **Backend Verification**:
   - `backend/app/api/deps.py:get_current_user` extracts the token.
   - `backend/app/core/security.py:verify_clerk_token` fetches and caches Clerk's JWKS public keys, validates the signature and expiration (`verify_exp: True`, `verify_aud: False`, `verify_at_hash: False`).
4. **JIT User Provisioning**:
   - `user_service.get_or_create_from_clerk_claims` checks if a user with `clerk_id` exists in PostgreSQL.
   - If missing, it inserts a new `User` record into PostgreSQL and attaches it to the request session.

---

### B. Document Upload & Asynchronous Ingestion Pipeline

```mermaid
sequenceDiagram
    autonumber
    actor User as Scholar (Frontend)
    participant API as FastAPI Backend
    participant DB as PostgreSQL
    participant Redis as Redis Broker
    participant Celery as Celery Worker
    participant LG as LangGraph Pipeline
    participant Qdrant as Qdrant Vector DB
    participant Neo4j as Neo4j Graph DB
    participant LLM as LLM Engine

    User->>API: POST /api/v1/documents/upload (PDF/TXT + mode)
    API->>DB: Save Document (status: 'pending') & IngestionJob
    API->>Redis: Enqueue process_document(doc_id)
    API-->>User: 202 Accepted (Document metadata)

    User->>API: WS /ws/documents/{doc_id}/progress
    API->>Redis: Subscribe to doc:{doc_id}:progress

    Redis->>Celery: Dequeue task
    Celery->>LG: invoke(initial_state)

    %% Step 1: Parse
    LG->>LG: 1. parse_node (pypdf/txt extraction)
    LG->>Redis: Publish progress (15%, "Parsing document pages...")
    Redis-->>User: WS Event (current_step: 'parse')

    %% Step 2: Chunk
    LG->>LG: 2. chunk_node (Sliding window: 550 tokens, 80 overlap)
    LG->>Redis: Publish progress (30%, "Splitting semantic chunks...")
    Redis-->>User: WS Event (current_step: 'chunk')

    %% Step 3: Extract
    LG->>LLM: 3. extract_node (Structured Entities/Relations or Study Hierarchy)
    LLM-->>LG: Extracted concepts, relationships & hierarchy
    LG->>Redis: Publish progress (50%, "Extracting concepts...")
    Redis-->>User: WS Event (current_step: 'extract')

    %% Step 4: Embed
    LG->>Qdrant: 4. embed_node (FastEmbed 384-dim vectors for chunks & entities)
    LG->>Redis: Publish progress (75%, "Indexing dense vectors...")
    Redis-->>User: WS Event (current_step: 'embed')

    %% Step 5: Graph
    LG->>Neo4j: 5. graph_node (Upsert nodes & relationships)
    LG->>Redis: Publish progress (85%, "Constructing knowledge graph...")
    Redis-->>User: WS Event (current_step: 'cluster')

    %% Step 6: Summarize
    LG->>LLM: 6. summarize_node (Community clustering & synthesis)
    LLM-->>LG: Community summaries & ratings
    LG->>Neo4j: Upsert community nodes & links
    LG->>Redis: Publish progress (92%, "Synthesizing communities...")
    Redis-->>User: WS Event (current_step: 'summarize')

    %% Step 7: Finalize
    LG->>DB: 7. finalize_node (Document status: 'ready', stats updated)
    LG->>Redis: Publish progress (100%, "Knowledge Map ready")
    Redis-->>User: WS Event (current_step: 'done', 100%)
```

---

### C. Town Explorer & Cartographic Layout
1. **Route Activation**: User navigates to `/realm/:documentId` (`TownExplorerView.vue`).
2. **Data Hydration**:
   - `documentsStore.fetchDocuments()` provides document source mode.
   - `graphStore.loadGraph(documentId, mode)` fetches `/api/v1/graph/{documentId}/town`.
3. **Cartography Algorithm (`useTownLayout.ts`)**:
   - Converts graph topology into isometric canvas coordinates:
     $$x = (g_x - g_y) \cdot \frac{\text{TILE\_W}}{2} + \text{CENTER\_X}$$
     $$y = (g_x + g_y) \cdot \frac{\text{TILE\_H}}{2} + \text{CENTER\_Y}$$
   - Arranges buildings via spiral distribution or community district clusters.
   - Calculates energy roads between connected nodes.
4. **Rendering**:
   - `TownCanvas.vue` renders SVG components:
     - `DistrictTurf.vue`: Base ground polygon for thematic communities.
     - `TowerBuilding.vue`: Isometric buildings sized by importance and colored by concept type.
     - `EnergyRoad.vue`: Connecting pathways with particle pulse animations.
     - `TreeCluster.vue`: Decorative environmental sprites.

---

### D. Regulus AI Guide (GraphRAG Conversational Retrieval)

```mermaid
flowchart LR
    UserQuery["User Asks Question\n(WebSocket /ws/chat/{session_id})"]
    Router{"Query Router\n(route_query)"}
    LocalSearch["Local Search\n- Qdrant Vector Search\n- Neo4j 1/2-Hop Subgraph\n- Text Chunks"]
    GlobalSearch["Global Search\n- Neo4j Community Clusters\n- LLM Community Summaries\n- Key Findings"]
    PromptBuilder["Build Grounded Prompt\n(System Prompt + Grounding Context)"]
    LLMStream["LLM Token Streaming"]
    ResponsePersist["Save Turn to Postgres\n- Assistant Content\n- Retrieved Subgraph IDs\n- Grounded Citations"]
    FrontendHighlight["Frontend Canvas Lights Up\nIlluminates Visited Towers & Roads"]

    UserQuery --> Router
    Router -- "Specific / Factoid" --> LocalSearch
    Router -- "Holistic / 'Summarize'" --> GlobalSearch
    LocalSearch --> PromptBuilder
    GlobalSearch --> PromptBuilder
    PromptBuilder --> LLMStream
    LLMStream --> ResponsePersist
    ResponsePersist --> FrontendHighlight
```

1. **Query Routing**:
   - Queries containing holistic keywords ("summarize", "overall", "main themes", "big picture") route to **Global Search**.
   - Direct conceptual queries route to **Local Search**.
2. **Local Search (`local_search.py`)**:
   - Converts query into vector embedding.
   - Queries Qdrant for top matching chunks and entities.
   - Traverses Neo4j for immediate neighbors and interconnecting relations.
3. **Global Search (`global_search.py`)**:
   - Queries Neo4j for community summary nodes.
   - Ranks community summaries against the topic using semantic relevance.
4. **Streaming Response**:
   - Tokens stream in real time to the browser via WebSocket.
   - A final completion payload delivers `citations` and `retrieved_subgraph: { node_ids: [...], edge_ids: [...] }`.
5. **Interactive Subgraph Illumination**:
   - The Pinia store (`useGraphStore`) updates `highlightedSubgraph`.
   - The canvas dynamically triggers pulsing neon glow rings on active towers and lights up energy roads.

---

### E. Study Mode Interactive Features
- **Sequential Learning Path (`LearningPathStepper.vue`)**:
  - Traverses prerequisite edges (`:PREREQUISITE_OF` or topological sort) to present a ordered walkthrough of concepts.
- **Deep Topic Dossier (`TopicReaderModal.vue`)**:
  - Displays summary, formulas/code snippets, prerequisites, and verbatim excerpts for any building.
- **Exam Gist Revision Sheet (`ExamGistModal.vue`)**:
  - Generates an instant high-yield cheat sheet with:
    - **High-Yield Rank** (Top 10 most critical concepts).
    - **Formulas to Memorize**.
    - **Likely Exam Questions**.
    - **Traps to Avoid**.

---

## 5. Comprehensive Codebase Directory Map

### Backend (`/backend/app`)

```
backend/app/
├── main.py                     # App factory, CORS, lifespan startup/shutdown hooks
├── core/
│   ├── config.py               # Pydantic BaseSettings (env vars, DB URLs, API keys)
│   └── security.py             # Clerk JWKS cache manager, RS256 JWT verifier, webhook svix
├── api/
│   ├── deps.py                 # FastAPI dependencies (get_current_user, get_db)
│   └── v1/
│       ├── router.py           # Master v1 API router assembling sub-routers
│       └── endpoints/
│           ├── auth.py         # GET /auth/me, POST /auth/webhook
│           ├── documents.py    # POST /documents/upload, GET /documents, DELETE /documents/{id}
│           ├── graph.py        # GET /graph/{doc_id}/town, /dossier/{node_id}, /exam-gist
│           ├── chat.py         # REST session management and message history
│           └── ws.py           # WebSockets: /ws/chat/{session_id}, /ws/documents/{doc_id}/progress
├── db/
│   ├── base.py                 # SQLAlchemy declarative base combining all models
│   ├── session.py              # PostgreSQL engine and SessionLocal session factory
│   ├── neo4j.py                # Neo4j Driver singleton, constraint & index initializer
│   └── qdrant.py               # Qdrant client singleton, collections setup
├── models/                     # SQLAlchemy ORM Models
│   ├── user.py                 # User (clerk_id, email, names, is_active)
│   ├── document.py             # Document, DocumentLink, IngestionJob
│   └── chat.py                 # ChatSession, ChatMessage
├── schemas/                    # Pydantic Request/Response Models
│   ├── auth.py                 # User profile schemas
│   ├── document.py             # Upload schemas, DocumentResponse, IngestionJobResponse
│   ├── graph.py                # TownGraphResponse, TopicDossierResponse, ExamGistResponse
│   └── chat.py                 # ChatSessionCreate, ChatMessageResponse
├── services/
│   ├── user_service.py         # JIT user creation and sync
│   ├── document_service.py     # Document record management & storage handling
│   ├── graph_service.py        # Neo4j Cypher queries for upserting and reading graphs
│   ├── parser.py               # pypdf extraction & sliding-window semantic chunker
│   ├── chat_service.py         # Query router, message persistence, LLM token streaming
│   ├── ingestion/
│   │   └── pipeline.py         # 7-node LangGraph State Machine
│   └── retrieval/
│       ├── local_search.py     # Hybrid vector + 2-hop neighborhood expansion
│       ├── global_search.py    # Community report hierarchical synthesis
│       └── study_features.py   # Learning path ordering, Dossiers & Exam Gist extractors
├── tasks/
│   ├── celery_app.py           # Celery instance config & Redis telemetry pub/sub
│   └── ingestion.py            # Async Celery task `tasks.process_document`
└── llm/
    ├── client.py               # Model factory (ChatOpenAI / ChatAnthropic / Gemini)
    ├── embeddings.py           # FastEmbed embedding service (BAAI/bge-small-en-v1.5)
    └── prompts.py              # System prompts & Pydantic structured output schemas
```

---

### Frontend (`/frontend/src`)

```
frontend/src/
├── main.ts                     # Vue app initialization, Clerk plugin, Pinia, Router
├── App.vue                     # Root component with router-view
├── style.css                   # Tailwind imports and custom typography
├── api/
│   └── client.ts               # Axios instance with Clerk auth interceptor
├── router/
│   └── index.ts                # Vue Router with navigation guards (auth/public routes)
├── stores/                     # Pinia State Management
│   ├── auth.ts                 # Backend user state, syncWithBackend()
│   ├── documents.ts            # Documents list, active document, upload actions
│   ├── graph.ts                # Nodes, edges, communities, learning path, dossier, exam gist
│   ├── chat.ts                 # Chat sessions, messages, active citations
│   └── player.ts               # Scholar XP, level, unlocked districts
├── composables/
│   ├── useTownLayout.ts        # Isometric coordinate projection & spiral layout
│   ├── usePanZoom.ts           # Canvas drag, zoom, and recenter gestures
│   ├── useGraphHighlight.ts    # Node/edge illumination and active filter matching
│   └── useWebSocket.ts         # Resilient WebSocket connection wrapper
├── views/
│   ├── HomeView.vue            # Dashboard with realms, upload panel, construction progress
│   ├── TownExplorerView.vue    # Full-screen isometric canvas + HUD overlays
│   ├── LoginView.vue           # Clerk SignIn screen
│   └── RegisterView.vue        # Clerk SignUp screen
├── components/
│   ├── home/                   # Dashboard Widgets
│   │   ├── TopHudHeader.vue    # App header, connection badge ('Backend Synced' / 'Local Dev')
│   │   ├── SourceUploadPanel.vue # PDF/TXT drag-and-drop uploader with mode selector
│   │   ├── RealmCard.vue       # Ingested realm card with stats and explore button
│   │   ├── ConstructionPipeline.vue # Live progress bar for documents being processed
│   │   └── FilterChips.vue     # Mode filter toggle (Research vs Study)
│   ├── town/                   # Isometric Canvas & SVG Elements
│   │   ├── TownCanvas.vue      # Main SVG viewport with pan/zoom container
│   │   ├── TowerBuilding.vue   # Concept building / tower with heights & labels
│   │   ├── EnergyRoad.vue      # Animated connector road between buildings
│   │   ├── DistrictTurf.vue    # Community background polygonal turf
│   │   ├── TreeCluster.vue     # Environmental foliage decorations
│   │   └── FloatingMascot.vue  # Interactive guide avatar floating over the town
│   └── hud/                    # Overlays & Interaction Panels
│       ├── TownNavBar.vue      # Canvas navigation controls, search, zoom buttons
│       ├── RegulusPanel.vue    # Floating AI Guide chat drawer with citations
│       ├── BuildingInfoCard.vue# Right-side drawer for inspecting selected nodes
│       ├── LearningPathStepper.vue # Stepper for sequential prerequisite traversal
│       ├── TopicReaderModal.vue# Deep-read topic dossier with excerpts & formulas
│       └── ExamGistModal.vue   # High-yield exam cheat sheet modal
```

---

## 6. Environment Configurations

### Backend (`backend/.env`)

| Variable | Description | Example |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5433/graphrag` |
| `NEO4J_URI` | Neo4j Bolt protocol URI | `bolt://localhost:7687` |
| `NEO4J_USER` | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | `changeme` |
| `QDRANT_URL` | Qdrant vector database URL | `http://localhost:6333` |
| `REDIS_URL` | Redis URL for Celery & Pub/Sub | `redis://localhost:6379/0` |
| `CLERK_JWKS_URL` | Clerk JWKS public key endpoint | `https://<tenant>.clerk.accounts.dev/.well-known/jwks.json` |
| `CLERK_SECRET_KEY` | Clerk backend API secret key | `sk_test_...` |
| `CLERK_WEBHOOK_SECRET`| Svix signature secret for webhooks | `whsec_...` |
| `OPENAI_API_KEY` | OpenAI API key for LLM calls | `sk-...` |
| `ANTHROPIC_API_KEY` | Anthropic API key (alternative) | `sk-ant-...` |
| `LLM_PROVIDER` | Active LLM provider (`openai` \| `anthropic`) | `openai` |

### Frontend (`frontend/.env.local`)

| Variable | Description | Example |
|---|---|---|
| `VITE_API_URL` | FastAPI backend base URL | `http://localhost:8000` |
| `VITE_CLERK_PUBLISHABLE_KEY` | Clerk frontend publishable key | `pk_test_...` |
| `VITE_BYPASS_AUTH` | Allow offline local development without Clerk | `false` |

---

## 7. Protocol for Future Codebase Changes

To keep this documentation accurate and valuable:

1. **New API Endpoints**:
   - Add route definition to `ARCHITECTURE.md` (§5).
   - Document any new Request/Response schemas.
2. **Database Migrations / Schema Changes**:
   - Update the table or Neo4j label descriptions in §3.
3. **Pipeline Modifications**:
   - If steps are added to `backend/app/services/ingestion/pipeline.py`, update §4.B.
4. **Log the Change**:
   - Append an entry to the **Change History & Evolution Log** (§8) below with the date, files touched, and rationale.

---

## 8. Change History & Evolution Log

| Date | Author / Agent | Changes Made | Files Modified |
|---|---|---|---|
| **2026-09-30** | Antigravity AI | Initial creation of comprehensive system architecture gist, component blueprints, and pipeline sequences. Documented system clock skew fix and Google OAuth `at_hash` bypass. | `ARCHITECTURE.md`, `README.md`, `security.py`, `client.ts`, `deps.py`, `TopHudHeader.vue` |
| | | *(Future changes will be appended here)* | |

