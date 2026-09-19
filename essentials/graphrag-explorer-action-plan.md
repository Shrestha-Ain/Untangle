# Untangle — Build Action Plan (Two-Person, Feature-by-Feature)

**Stack:** Vue 3 + TS (frontend) · FastAPI (backend) · Neo4j · PostgreSQL · Qdrant · Redis + Celery · Clerk (auth) · Anthropic/OpenAI (LLM) · Research & Study Modes

**How to use this doc:** work top-to-bottom. Each phase is one deployable increment — don't start Phase N+1 until Phase N's "Definition of Done" is checked off. Every phase splits into a **Person A (Backend/Data)** track and a **Person B (Frontend/UX)** track that run *in parallel*, syncing at the API contract. Roles are fixed by track, not by person, so both people touch backend and frontend work roughly equally over the whole project — swap who leads which track every ~2 phases if you want literal 50/50 exposure to both sides.

Legend: 🔧 Person A (Backend/Data/Infra) · 🎨 Person B (Frontend/UX/Vue) · 🤝 Pair/sync point

---

## Phase 0 — Foundations & Tooling
**Goal:** Empty-but-running skeleton both people can build on independently from day one.

- 🤝 Agree on the API contract shape (REST + WS endpoint list from the system design doc), repo structure (monorepo: `/frontend`, `/backend`), and Git workflow (feature branches, PR review).
- 🔧 Scaffold `backend/` per the FastAPI layout (`app/core`, `api/v1`, `services`, `tasks`, `llm`, `db`). Set up `docker-compose.yml` with Postgres, Neo4j, Qdrant, Redis stubs. Add `pydantic-settings` config + `.env.example`.
- 🎨 Scaffold `frontend/` with Vite + Vue 3 + TS + Pinia + Tailwind. Wire up the design tokens from the design spec (colors, fonts: Inter/JetBrains Mono, spacing, shadows) as a Tailwind config + CSS variables layer. Build the empty `LoginView`, `RegisterView`, `HomeView`, `TownExplorerView` route shells with the router.
- 🤝 Set up GitHub Actions: lint (`ruff`, `eslint`) + type-check (`vue-tsc`) + backend unit test stub on PR.

**Definition of Done:** `docker-compose up` boots all 5 services; `npm run dev` serves an empty routed Vue app; CI passes on an empty PR.

---

## Phase 1 — Auth (Clerk) & App Shell
**Goal:** A real user can sign up, log in, and land on a protected dashboard shell. This replaces the hand-rolled JWT auth in the original design with Clerk end-to-end.

- 🔧 Create the Clerk application (dashboard), get publishable + secret keys. In FastAPI, add a dependency (get_current_user in api/deps.py) that verifies the Clerk session JWT using the official clerk-backend-api SDK. No manual JWKS implementation needed — the SDK handles key rotation. Add a Clerk webhook endpoint (/webhooks/clerk) to create/update local user rows in Postgres on user.created/user.updated events.
- 🎨 Install `@clerk/vue`, wrap the app in `<ClerkProvider>`, build `LoginView`/`RegisterView` using Clerk's `<SignIn>`/`<SignUp>` components restyled to match the Untangle sign-in page (warm neutral background, subtle dot grid, muted palette). Add the router navigation guard that redirects unauthenticated users to login, and attaches the Clerk session token to outgoing API calls (axios/fetch interceptor).
- 🤝 Verify end-to-end: sign up in the UI → row appears in Postgres `users` → protected backend route returns 401 without a token and 200 with one.

**Definition of Done:** Full sign-up → login → protected dashboard route round-trip works; no manual JWT code remains.

---

## Phase 2 — Document Upload & Dashboard Shell
**Goal:** A logged-in user can upload a file and see it listed with a status.

- 🔧 Postgres schema for `documents` + `jobs` (per system design §5.2). The Postgres documents table must include a source_mode column ('research' | 'study') — this is stored at upload time based on which mode the user selected in the UI. Build `POST /documents/upload` (multipart, file-type/size validation, stores file, inserts `documents` row with `status=pending`, enqueues a placeholder Celery job) and `GET /documents` / `GET /documents/{id}` / `DELETE /documents/{id}`.
- 🎨 Build `HomeView` (Untangle dashboard): dual-mode SourceUploadPanel (left = Research Mode paper upload, right = Study Mode book upload), document list/MapCard grid bound to `GET /documents` via a `documents` Pinia store. Wire delete + basic empty/loading states.
- 🤝 Confirm upload → row appears with `pending` status → visible instantly in the UI list (simple refetch is fine for now; live progress comes in Phase 4).

**Definition of Done:** Upload a PDF/TXT/DOCX from the UI, see it appear in the dashboard with a status column.

---

## Phase 3 — Parsing, Chunking & Async Pipeline Skeleton
**Goal:** Uploaded documents actually get processed into text chunks, asynchronously.

- 🔧 Wire Celery + Redis broker for real. Implement the ingestion **chain** skeleton (`parse.s() | chunk.s()`) using `unstructured` (or `pypdf`/`python-docx`) for parsing and a sentence-aware splitter (~500–800 tokens, ~15% overlap) for chunking. Write `Chunk` nodes + `HAS_CHUNK` edges to Neo4j. Update `jobs`/`documents.status` at each step (`parsing` → `chunking`).
- 🎨 Build the WebSocket client composable (`useWebSocket.ts`) and a simple progress UI (`IngestionProgress` component, 3-step visual (step labels are mode-aware: Research = Parse → Extract Entities → Cluster Communities; Study = Parse → Extract Chapter Hierarchy → Link Concepts)) that connects to `/ws/documents/{id}/progress` and reflects live status on the `MapCard`.
- 🔧 Implement `/ws/documents/{id}/progress`: FastAPI subscribes to the Redis `progress:{document_id}` channel and relays events.
- 🤝 Upload a real multi-page doc, watch the progress bar move from parsing → chunked live in the UI.

**Definition of Done:** Uploading a document visibly and correctly progresses through parse/chunk stages in real time in the browser.

---

## Phase 4 — LLM Entity/Relationship Extraction
*Note: This phase applies to Research Mode documents (source_mode='research'). Study Mode documents follow a different extraction path described in Phase 4B.*
**Goal:** Chunks become graph facts.

- 🔧 Build `llm/client.py` (swappable provider wrapper) and `llm/prompts.py` extraction prompt (structured JSON: entities + relationships). Implement the per-chunk extraction step as a Celery **group** (fan-out), using the cheap/fast model (Haiku) per system design §14. Write results into Neo4j via the idempotent `MERGE` Cypher pattern. Update pipeline status to `extracting`.
- 🎨 Build a minimal **read-only graph debug view** (a simple table or basic Cytoscape.js render of raw nodes/edges for a document) so extraction quality is visible without waiting for the full Town Canvas — this doubles as a sanity-check tool for Person A too.
- 🤝 Run one real document end-to-end through parse → chunk → extract, inspect the resulting graph in Neo4j Browser or the debug view together.

**Definition of Done:** A test document produces a plausible, inspectable entity/relationship graph in Neo4j.

---

## Phase 4B — Study Mode: Structural Hierarchy Extraction
**Goal:** Books become navigable hierarchical knowledge maps.

- 🔧 Implement the Study Mode extraction pipeline: LLM extracts chapter → section → topic → subtopic hierarchy (instead of NER-based entity extraction). Build the second LLM pass for concept relationship linking (CONCEPTUALLY_LINKS edges). Implement auto-suggestion of external sources for topics flagged with needs_context=True: embed the topic description, Qdrant search across user library, send source_suggestion WebSocket events. Build `GET /graph/{document_id}/study-map` returning buildings/roads in the same format as the Research Mode `/town` endpoint.
- 🎨 The `TownCanvas.vue` requires no changes — it reads the same building/road format. Only the label semantics differ (district label shows chapter name, not community name). Add a `ModeLabel.vue` component that displays the current mode's semantic labels (shown in the top HUD).
- 🤝 Upload a real textbook chapter, inspect the resulting hierarchy in Neo4j and the study map in the canvas.

---

## Phase 5 — Entity Resolution & Deduplication
**Goal:** The graph doesn't have five nodes for "Obama."

- 🔧 Implement the three-tier dedup: exact case-insensitive match, embedding-similarity candidate merge (threshold ~0.88), and LLM disambiguation for borderline cases (0.75–0.88), followed by `apoc.refactor.mergeNodes`. Add this as the `dedupe` Celery step (chord callback after the extraction group finishes).
- 🎨 Extend the debug graph view with a simple "before/after dedup" node count indicator, and start the `graph.ts` Pinia store + `GET /graph/{document_id}` API contract discussion (even though the real Town Canvas UI comes later) so the data shape is agreed before Phase 8/11.
- 🤝 Review dedup precision/recall together on 2–3 real documents; tune thresholds.

**Definition of Done:** Duplicate-entity count drops measurably on a test corpus; merge logic is idempotent on re-run.

---

## Phase 6 — Embeddings & Vector Store
**Goal:** Semantic search over chunks and entities works.

- 🔧 Integrate embedding generation (open-source `bge-small-en-v1.5` or a paid API — pick per cost tolerance) into the pipeline; upsert into Qdrant `chunks` and `entities` collections after dedup. Add the `embed` Celery step. Expose a simple internal test endpoint or script for ad-hoc vector search.
- 🎨 Build the **Evaluation Report page shell** (routes + static layout only per design spec §3.4/§4) — no real data yet, just the two-combatant-card layout and empty chart containers. This is a good isolated frontend task while Person A is deep in embedding plumbing.
- 🤝 Sanity-check: query a known phrase, confirm the top-k Qdrant results make sense.

**Definition of Done:** Every ingested document has chunk + entity embeddings queryable in Qdrant.

---

## Phase 7 — Community Detection & Summarization
*Note: This phase applies to Research Mode only. Study Mode documents skip this step — their structural hierarchy (chapters → sections → topics) serves the equivalent role.*
**Goal:** The graph gets hierarchical "districts" with LLM summaries.

- 🔧 Run Leiden clustering via Neo4j GDS, write `Community` nodes + `BELONGS_TO`/`PARENT_OF` edges. Implement community summarization (LLM call per community). Add `cluster` and `summarize` Celery steps, finalize pipeline (`status=ready`).
- 🎨 Build the **Community Browser** panel (right sidebar list from the Explorer View mock: community name, entity count, summary snippet, expandable) bound to a new `GET /graph/{document_id}/communities` endpoint contract — build against mocked JSON first if backend isn't ready yet.
- 🤝 First fully-automatic end-to-end run: upload → `status=ready` with communities and summaries, no manual intervention.

**Definition of Done:** A document reaches `ready` status unattended, with real community summaries visible via API.

---

## Phase 8 — Local Search (Query Pipeline, Part 1)
**Goal:** Specific, entity-anchored questions get real answers.

- 🔧 Implement query classification (local vs. global), local search retrieval (seed entities via Qdrant → N-hop Neo4j expansion via `apoc.path.subgraphAll` → hybrid chunk retrieval → LLM synthesis with citations). Build `POST /chat/sessions` and a first synchronous (non-streaming) `POST`-style version of chat before adding WebSocket streaming, to de-risk correctness first.
- 🎨 Build the **Chat Panel shell** (message list, input box, session creation) per the Explorer View mock, calling the synchronous chat endpoint for now. Render citations as simple footnote links.
- 🤝 Ask 5–10 real questions against a real ingested doc together; sanity-check answer quality and citation correctness before adding complexity.

**Definition of Done:** A user can ask a specific question in the UI and get a cited, correct-ish answer (non-streaming is fine here).

---

## Phase 9 — Global Search + Streaming Chat
**Goal:** Broad thematic questions work, and answers stream token-by-token.

- 🔧 Implement global search (map-reduce over community summaries). Convert chat to `WS /ws/chat/{session_id}`: stream tokens, then send the final `{answer, citations, subgraph, search_mode, latency_ms}` payload. Persist `chat_messages` with `retrieved_subgraph` JSONB.
- 🎨 Wire the Chat Panel to the WebSocket: token-by-token rendering ("Streaming" badge from the mock), search-mode toggle (Local/Global), and store the `subgraph` payload in the `graph` Pinia store for later highlighting.
- 🤝 Verify a genuinely multi-hop question resolves better via global search than local — this is the project's core value proposition, worth confirming explicitly.

**Definition of Done:** Chat streams live in the UI for both local and global modes; subgraph payload is captured client-side per message.

---

## Phase 10 — Graph Canvas: Base Town Rendering
**Goal:** The knowledge graph renders as the isometric Untangle knowledge map — static first, no interactivity yet.

- 🔧 Build `GET /graph/{document_id}/town` (for Research Mode) and `GET /graph/{document_id}/study-map` (for Study Mode): town-formatted payload (entities as typed/leveled buildings with computed positions, relationships as roads). Use Cytoscape.js headless (backend or a build script) to compute a force-directed layout, then project into isometric grid coordinates — decide together whether this layout math lives in the backend or a frontend composable (`useTownLayout.ts`); either is fine, just pick one owner.
- 🎨 Build `TownCanvas.vue`, `TowerBuilding.vue`, `EnergyRoad.vue`, `DistrictTurf.vue` per the component library (SVG, type-colored, ground-shadow, floating `TowerTag`). Render a static town for one real document. Add `usePanZoom.ts` for pan/zoom.
- 🤝 Look at a real document's town together and eyeball whether the layout is legible (declutter top-N by mention count for towns >500 entities, per system design §10).

**Definition of Done:** Opening a document's Explorer view shows its town, correctly typed/colored, pannable and zoomable, no console errors.

---

## Phase 11 — Interactivity: Learning Path Stepper, Deep Topic Reader & Subgraph Highlight
**Goal:** The town responds to clicks, chat answers, and structured guided curriculum traversal.

- 🔧 Finalize `GET /graph/{document_id}` (full graph pagination) and `GET /graph/{document_id}/communities` for real. Build `GET /graph/{document_id}/learning-path` (topological dependency sequence) and `GET /graph/{document_id}/nodes/{id}/dossier` (aggregating all raw chunks, formulas, and synthesis for that concept). Ensure the chat WS payload's `subgraph.node_ids`/`edge_ids` map cleanly onto the town's building/road IDs.
- 🎨 Build `BuildingInfoCard.vue` (click building → slide-in detail + "Read Full Topic Dossier" button). Build `TopicReaderModal.vue` providing an exhaustive reading view of all chunks, formulas, and connections for that topic. Build `LearningPathStepper.vue` (`[Prev] Step X of N [Next]`) and the illuminated dashed curriculum path on `TownCanvas.vue`. Implement `useGraphHighlight.ts` for AI answer illumination.
- 🤝 Run the full demo flow together: traverse the learning path from Step 1 to N → open the topic reader to study raw chunks → ask Regulus a question → watch the map light up.

**Definition of Done:** Guided learning path advances smoothly, selecting any topic opens the comprehensive reader dossier with real source chunks, and asking Regulus visibly highlights the exact subgraph used.

---

## Phase 12 — Evaluation Harness & Report
**Goal:** Turn the demo into a defensible, quantified result.

- 🔧 Build the gold test set (20–30 Q/A pairs, some genuinely multi-hop), the plain vector-RAG baseline arm, and the scoring pipeline (LLM-as-judge accuracy, faithfulness check, multi-hop-vs-single-hop split, latency p50/p95, cost per doc/query). Build `GET /eval/report` and persist results to `/eval/results_v1.md`.
- 🎨 Wire the Evaluation Report page (shelled in Phase 6) to real `/eval/report` data: accuracy/latency/cost charts (Chart.js/ApexCharts), the run-history table, and the benchmark results banner.
- 🤝 Run the evaluation together, discuss the actual numbers, and agree on the headline stat for the README/resume bullet.

**Definition of Done:** `/eval/report` returns real numbers backed by `/eval/results_v1.md`, rendered correctly on the Evaluation Report page.

---

## Phase 13 — Deployment, Hardening, Docs
**Goal:** Ship it.

- 🔧 Security pass (rate-limit `/chat` and `/documents/upload` via `slowapi`, confirm parameterized Cypher everywhere, scope all queries by `user_id`/`document_id`, review file-upload validation). Deploy backend+Celery to Railway/Render, Neo4j to AuraDB Free, Postgres to Supabase/Railway, Redis to Upstash, Qdrant to Qdrant Cloud Free. Finish CI/CD (build/push images, auto-deploy on merge).
- 🎨 Deploy frontend to Vercel/Netlify, do a full responsive pass against the breakpoint table (desktop/tablet/mobile behaviors from design spec §5), fix any prod-only CORS/env issues, record the demo video/GIF for the README.
- 🤝 Write the README together (architecture diagram, resume bullets, evaluation numbers, setup instructions), do a final full walkthrough on the deployed URL as if demoing to an interviewer.

**Definition of Done:** A stranger can open the deployed link, sign up via Clerk, upload a document, chat with it, and see the town light up — with zero local setup.

---

## Stretch Goals (post-v1, split however you like)
- Incremental re-ingestion without a full rebuild.
- Multi-document cross-referencing (shared entity graph across documents).
- Second LLM provider A/B comparison for the eval report.
- "Why did you say that" Cypher/retrieved-chunk trace view.
- Cross-source context linking UI: when Regulus detects a concept needing outside context, surface a source suggestion card in the Regulus Panel with one-click import.

## Scope-Cutting Order (if time runs short)
1. Cut global search first — local search alone is still a strong demo.
2. Cut Celery for FastAPI `BackgroundTasks` + polling instead of WebSocket progress push.
3. Cut the open-source embedding model for a paid API (less setup, small ongoing cost).
