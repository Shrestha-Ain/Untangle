# Untangle — GraphRAG Knowledge Mapping Tool

Turn research papers and textbooks into interactive, explorable knowledge maps. Upload academic material, watch it get transformed into an isometric map of entities, topics, and their relationships, and query it through **Regulus**, an AI guide that reasons across the graph and highlights exactly what it used to answer.

**Stack:** Vue 3 · TypeScript · Vite · Tailwind CSS · FastAPI · Neo4j · PostgreSQL · Qdrant · Redis · Celery · Clerk

**Two modes:**
- **Research Mode** — Papers → entity/relationship/community knowledge maps
- **Study Mode** — Books/textbooks → chapter → section → topic hierarchy maps

### Key Features & Innovations:
- **Dark & Light Mode Support**:
  - Global theme manager (`useThemeStore`) supporting seamless switching between Dark Mode and Light Mode with `localStorage` persistence.
  - Full Tailwind `class` mode across all UI modals, drawers, HUD navigation, and cards.
  - Three.js 3D WebGL scene dynamically adapts: Midnight Charcoal (`0x090D16`) for dark mode and Crisp Pearl White (`0xF8FAFC`) for light mode, updating the ground plane and coordinate grid in real time.
  - Easily toggle modes with a single click from the Top HUD on the landing page or the 3D Town Navigation Bar.
- **Interactive Mouse Sparkles & High-Impact Landing Page**:
  - Interactive 60fps canvas (`InteractiveSparkles.vue`) that spawns glittering multi-colored stars, diamonds, and glowing particles following cursor and touch movements.
  - Celebratory 24-sparkle burst explosion on click.
  - Hero section inspired by spatial memory and cognitive science ("Turn Dense Papers & Textbooks into Living 3D Knowledge Towns", "Never drown in a 40-page PDF again").
- **True 3D WebGL Three.js Town Engine & Unidirectional Road Arrows**:
  - Full WebGL 3D canvas featuring **OrbitControls** allowing the user to freely **orbit 360°** (left-click drag), **pan** across the realm (right-click drag), and **zoom** into any structure (scroll wheel).
  - **Flat Architectural Building Tops**: Strictly flat, stepped cubic terraces, observation decks, corner battlements, and helipads (zero cones, pyramids, or domes).
  - **Elevated Directional Arrows**: High-contrast arrows along the learning path viaducts are strictly **unidirectional from lower step to higher step**; if and only if steps are interchangeable, prominent amber **bidirectional arrows** appear. All arrowheads are elevated above road geometry (`pos.y += 6.5`) so they never hide behind road tubes.
  - Razor-sharp 2D HTML/CSS holographic step badges projected in 3D space (`vector.project(camera)`) with camera occlusion checking.
  - One-click camera presets for **3D Isometric View**, **Top-Down View**, **Focus on Node**, and **Recenter**.
- **Fully Movable & Resizable Floating Dialogs (Hover-Only Tooltips)**:
  - **Top Step Slider** (`LearningPathStepper`): Drag anywhere on the screen by its grip header; resize width and height from multi-directional edges or corners; snap back with one-click reset.
  - **Regulus AI Chat Guide** (`RegulusPanel`): Freely reposition anywhere on the viewport (left, right, top, bottom); stretch width and height to read long derivations comfortably; docked capsule initially so the full 3D town is 100% visible.
  - **Topic Detail Drawer** (`BuildingInfoCard`): Move to the left or right side of the screen; resize freely to fit notes and formulas; minimize to a floating pill.
  - **No Clutter Text**: Removed static `(Draggable & Resizable)` text; subtle indicator tags only appear when hovering directly over drag grips or resize edges.
- **Vibrant Solid Color Aesthetic (Strictly NO Gradients)**:
  - Eliminated fuzzy gradients and muted palettes in favor of crisp, vibrant, high-contrast solid color blocking:
    - 🟢 Emerald (`#10B981`): Learning paths, Foundations, Quiz Master
    - 🔵 Cyan (`#06B6D4`): Concept & Topic Towers, Road tubes
    - 🟣 Royal Purple (`#8B5CF6`): Person & Author towers, Interactive Checks
    - 🟡 Sunburst Amber (`#F59E0B`): Section towers, Personal Notes, Analogies
    - 🔴 Crimson (`#EF4444`): High-Yield Exam Gists, Exam Traps
    - 🔷 Cobalt Blue (`#2563EB`): Organization & Institution towers
    - ⬛ Midnight Charcoal (`#090D16` / `#0F172A`) & ⬜ Pure White (`#FFFFFF`): High-contrast framing and solid 2px borders.
- **Soothing Bluish Theme & Cohesive Palette Across Whole Site**:
  - Harmonized bluish aesthetic in both dark and light modes:
    - **Dark Mode**: Deep midnight slate-navy (`#0B1120`, `#0F172A`, `#111C35`), soft icy text (`#F8FAFC`, `#E2E8F0`), royal sapphire (`#2563EB`), vibrant sky cyan (`#38BDF8`), and slate-navy borders (`#1E293B`, `#334155`).
    - **Light Mode**: Soothing frost blue canvas (`#F0F4F8`), pure elevated white cards with slate borders (`#E2E8F0`, `#DBEAFE`), cobalt blue brand accents (`#2563EB`), and deep navy text (`#0F172A`).
  - Smooth transitions across all components with full dark/light toggle sync.
- **Failproof Pedagogical AI Chatbot Overhaul (Regulus)**:
  - Robust multi-stage string sanitization in both backend (`clean_llm_text`) and frontend (`cleanAssistantContent`) completely eliminates Python AST string wrappers (`[{'type': 'text', 'text': ...}]`), unescapes literal `\n` into real linebreaks, and purges robotic meta-commentary disclaimers (e.g. "As the local context chunks contain no direct text...").
  - Formats responses into intuitive learning modules: 💡 **Real-World Analogy**, ⚙️ **Under the Hood (Formulas & Code)**, 🗺️ **Position in Curriculum**, ⚠️ **High-Yield Exam Trap**, and 💬 **Interactive Check**.
  - **Live Clickable Follow-Up Chips**: Follow-up questions (`👉`) are rendered as interactive, clickable pill buttons that can be tapped to immediately ask that question in the chat.
  - 🎯 **Topic Focus**: Scoped strictly to the active selected tower (checks local definition, formulas, and 1-hop connections first without dumping textbook overviews).
  - 📄 **Document RAG**: Searches across the full document knowledge graph and verbatim text chunks.
  - 🌐 **Worldwide AI**: Explores expansive global engineering and scientific knowledge beyond the document.
  - **Model Switcher**: Seamlessly switch between `⚡ Flash` (speed) and `🧠 Sonnet / Pro` (deep reasoning).
- **Interactive Gamified Quiz Master & Personal Notes**:
  - Take instant 4-option multiple-choice quizzes with explanations for either a specific topic or the entire document.
  - Write, persist, and export personal notes for individual topics or the full document to Markdown.
- **Study Progress & Topic Completion Percentage Tracker**:
  - Global `useProgressStore` with `localStorage` persistence (`untangle_study_progress`) keyed by document ID.
  - Real-time study completion percentage indicator (`[ 📊 {percentage}% Mastered ]`) embedded in both the top navigation bar (`TownNavBar.vue`) and the movable learning path stepper (`LearningPathStepper.vue`).
  - Comprehensive **Study Progress Modal** (`StudyProgressModal.vue`) featuring:
    - Overall completion percentage gauge and animated solid progress bar.
    - Topic-by-topic mastery breakdown table with individual checkboxes to toggle studied status.
    - Quick-focus camera buttons (`near_me`) to glide directly to any building on the 3D map.
    - One-click "Mark All Completed" and "Reset Progress" controls.
  - Active step mastery toggle (`[ ✓ Mark Done / Mastered ]`) in the learning path stepper that automatically advances to the next prerequisite topic upon completion.
- **Differentiated Capabilities for Research Papers vs. College Study Materials**:
  - **Research Paper Mode**:
    - **Theoretical Novelty & Architectural Contribution**: Highlighted computational complexity breakthroughs (e.g. $O(1)$ sequential operations via parallel matrix multiplication vs. $O(N)$ recurrence in RNNs/LSTMs).
    - **Mathematical Formulations**: Display of core equations (e.g. $\text{MultiHead}(Q,K,V) = \text{Concat}(\text{head}_1, \dots, \text{head}_h)W^O$).
    - **Empirical Ablation Metrics**: Detailed ablation study benchmarks, parameter scaling numbers, and BLEU evaluation scores.
    - **Active BibTeX & arXiv Bridge**: Auto-generated formal BibTeX academic citations with a one-click clipboard copy button.
  - **College Study Material Mode**:
    - **Syllabus & Topic Mastery Tracking**: Real-time topic study completion toggle (`[ ✓ Mark Topic as Studied ]`) seamlessly synced with the overall course progress bar.
    - **Intuitive Analogies & Mental Models**: Real-world metaphors to grasp difficult engineering concepts.
    - **Implementation Snippets**: Concrete C kernel system calls (`fork()`, `execvp()`, `waitpid()`) and runnable algorithms.
    - **Professor Exam Traps**: High-yield warnings highlighting trick questions, edge cases, and exam pitfalls commonly tested in university exams.
- **Document-Grounded Exam Gist**: Generates accurate, high-yield exam sheets directly derived from the loaded document's graph nodes with classic exam questions, formulas, and common traps.
- **Realistic End-to-End Product Walkthrough Video (`DemoVideoModal.vue`)**:
  - Live in-browser guided simulation directly embedding the **actual Three.js WebGL 3D Town Canvas (`TownCanvas3D.vue`)** across 7 realistic chapters focusing centrally on **how Regulus AI gives intelligent structured replies after ingestion**:
    1. **Authentication & Dual-Mode Selection**: Clerk sign-in modal, verified identity badge, and instant access to either **Research Mode** (for arXiv papers) or **Study Mode** (for textbooks and syllabi).
    2. **Document Ingestion Pipeline**: Active PDF dropzone, document type detection, and 4-phase GraphRAG processing pipeline (chunking, entity extraction, vector embedding, and community synthesis) with live progress steppers.
    3. **The Actual 3D Knowledge Realm**: 100% full unobstructed WebGL 3D town with 360° orbital camera rotation, flat-roof stepped architectural towers, elevated energy viaducts with moving glowing photons, and live mouse orbit/zoom controls right inside the video player.
    4. **AI Replies After Ingestion (Core Highlight)**: Side-by-side interactive tab toggle showing the distinct responses of Regulus AI:
       - *Research Mode Tab*: Theoretical novelty, mathematical formulation, empirical ablation study metrics, and one-click BibTeX citation copy.
       - *College Study Mode Tab*: Intuitive real-world analogies, runnable C system call code, high-yield professor exam trap warnings, and clickable follow-up inquiry chips.
    5. **Top Learning Path Slider**: Interactive prerequisite stepper with Prev/Next buttons, active step cards, and real-time 3D camera auto-focus with a pulsating radar ring gliding directly to the target tower.
    6. **Study Progress & Topic Breakdown**: Live completion percentage gauge, mastery progress bar, and topic-by-topic checklist showing studied status and quick-focus camera buttons.
    7. **Quiz Master, Personal Notes, Theme Sync & Instant Launch**: Gamified 4-choice questions (+25 XP!), personal notes drawer with Markdown export, interactive dark/light theme switch with immediate 3D lighting adaptation, and direct one-click "Launch 3D Knowledge Realm" action.
  - Accompanied by a soothing female voice narration pipeline (`window.speechSynthesis` prioritizing Microsoft Jenny/Aria and Google Female with `pitch: 1.10`, `rate: 0.96`), Web Audio API harmonic sound effects, word-by-word synchronized subtitles, audio visualizer, chapter jump pills, scrubber timeline, and interactive 3D map controls.
  - One-click access via the clean **"Watch Demo Video"** hero button and home banner card.
- **Zero-Friction 3D Realm Explorer**:
  - The **"Explore 3D Realm"** button connects directly to backend knowledge endpoints (`/documents` and `/graph/{doc_id}/town`), supported by a unified route alias (`/realm/:documentId` and `/town/:documentId`).
  - Seamlessly provides canonical flagship knowledge realms (*"Attention Is All You Need"* in Research Mode and *"Operating Systems: Three Easy Pieces"* in Study Mode) with zero cold-start delay, even without database seeding.

---

## Prerequisites

| Tool | Min Version | Check |
|---|---|---|
| Python | 3.13+ | `python --version` |
| uv | any | `uv --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |

Install `uv` if you don't have it:
```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## Backend Setup (FastAPI + uv)

```bash
cd backend
uv venv
uv sync
cp .env.example .env
```

Open `.env` and fill in:

```env
# Database connections
DATABASE_URL=postgresql://user:password@localhost:5432/untangle
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
QDRANT_URL=http://localhost:6333

# Redis / Celery
REDIS_URL=redis://localhost:6379/0

# Clerk (backend JWT verification)
CLERK_SECRET_KEY=sk_test_...

# LLM API (use at least one)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

```bash
# Start the FastAPI dev server
uv run uvicorn app.main:app --reload --port 8000

# (Separate terminal) Start the Celery worker (use -P solo on Windows)
uv run celery -A app.tasks.celery_app worker --loglevel=info -P solo
```

API: **http://localhost:8000**  
Docs: **http://localhost:8000/docs**

> `uv run <command>` always uses the project's `.venv` — no manual activation needed.

---

## Frontend Setup (Vue 3 + Vite + Tailwind)

```bash
cd frontend
npm install
cp .env.example .env.local
```

Open `frontend/.env.local` and set:

```env
VITE_API_URL=http://localhost:8000
VITE_CLERK_PUBLISHABLE_KEY=pk_test_...
```

```bash
npm run dev
```

Frontend: **http://localhost:5173**

> In development, Vite proxies `/api/*` → `http://localhost:8000` and `/ws/*` → `ws://localhost:8000`. No CORS issues locally.

---

## Running Both Together

```bash
# Terminal 1
cd backend && uv run uvicorn app.main:app --reload --port 8000

# Terminal 2
cd frontend && npm run dev
```

Open **http://localhost:5173**, sign in with Clerk, and upload your first document.

---

## Useful Commands

### Backend
```bash
uv run pytest              # run tests
uv run ruff check .        # lint
uv run ruff format .       # format
uv add <package>           # add dependency
uv add --dev <package>     # add dev dependency
```

### Frontend
```bash
npm run build              # production build
npm run preview            # preview production build locally
npx vue-tsc --noEmit       # type-check without building
```

---

## Challenges Faced and How to Fix Them

### 1. Clock Skew / Out-of-Sync System Clock Causing Clerk JWT Failures (`401 Unauthorized`)

- **Symptom:**
  - After signing in via Clerk (e.g., Google OAuth or email), the UI continues showing `"Local Dev"` badge or fails to connect to the backend.
  - The backend logs `401 Unauthorized` on `GET /api/v1/auth/me` and other protected endpoints.
  - Token verification fails with `Token has expired` or signature rejection even immediately after logging in.

- **Root Cause:**
  - JWT tokens issued by Clerk include standard timestamp claims (`iat` for "Issued At" and `exp` for "Expiration").
  - If your local operating system clock drifts or is out of sync with internet standard time (NTP), `jwt.decode` on the backend validates the token timestamps against the local host machine's system time. A drifted clock causes immediate rejection of valid tokens.

- **How to Fix:**
  - **Windows:**
    1. Open **Settings** &rarr; **Time & Language** &rarr; **Date & Time**.
    2. Toggle **"Set time automatically"** to **On**.
    3. Click the **"Sync now"** button under *Additional settings*.
    4. Alternatively, open PowerShell as Administrator and run:
       ```powershell
       w32tm /resync
       ```
  - **macOS / Linux:**
    - On macOS:
      ```bash
      sudo sntp -sS time.apple.com
      ```
    - On Linux:
      ```bash
      sudo systemctl restart systemd-timesyncd
      # or
      sudo chronyd -q 'server pool.ntp.org iburst'
      ```
  - After re-synchronizing your system clock, hard refresh the browser (`Ctrl+Shift+R` or `Cmd+Shift+R`) and sign in again.

### 2. Google OAuth JWT `at_hash` Validation

- **Symptom:** Backend returns `401 Unauthorized` with `Invalid token: No access_token provided` during token decoding for users signing in through Google.
- **Root Cause:** Tokens issued via Google OAuth include an `at_hash` (access token hash) claim. By default, `python-jose` expects an `access_token` parameter when `verify_at_hash` is enabled.
- **How to Fix:** In `backend/app/core/security.py`, pass `"verify_at_hash": False` in the `jwt.decode()` options.

### 3. Running Without Docker Desktop (Offline Simulation Mode)

- **Why is Docker Desktop important?**
  - Docker Desktop runs PostgreSQL (port 5433), Neo4j (port 7687), Qdrant (port 6333), and Redis (port 6379). These containers power the full PDF ingestion, vector embeddings, and graph extraction pipelines.
  - If Docker Desktop is not started, backend database table creation and Celery workers will pause or defer connections.
- **Can I run the platform without Docker?**
  - **YES!** Untangle includes an offline demonstration simulation engine. When databases are offline, the frontend loads realistic knowledge graphs (OSTEP Operating Systems textbook and the Attention Transformer paper), complete with full 3D town rendering, sequential learning paths, Regulus pedagogical chatbot explanations, interactive quizzes, and personal notes.

---

## Recent Feature Highlights

1. **True 3D WebGL Knowledge Town Engine (`TownCanvas3D.vue`)**: Full Three.js 3D cartography featuring 360° OrbitControls (free orbit, pan, scroll zoom), flat-roof stepped architectural citadel monoliths (zero cones or domes), elevated unidirectional road arrows, holographic 2D step badges projected in 3D screen space, and one-click camera presets (Isometric, Top-Down, Node Auto-Focus, and Recenter).
2. **Movable & Resizable Floating UI Architecture (`useDraggableResizable.ts`)**: The top prerequisite stepper slider, Regulus AI chat window, and topic detail drawer can be freely dragged anywhere on the screen and resized from any border or corner, with subtle indicator tags appearing only on hover.
3. **Failproof Pedagogical Regulus AI Tutor**: Robust multi-stage string sanitization stripping Python AST wrappers (`[{'type': 'text'}]`), unescaping linebreaks, and eliminating robotic disclaimers. Outputs structured modules (💡 Real-World Analogy, ⚙️ Technical Mechanics, 🗺️ Position in Curriculum, ⚠️ High-Yield Exam Trap, and 💬 Interactive Check) with live clickable follow-up question chips (`👉`).
4. **Study Progress & Topic Completion Percentage Tracker (`StudyProgressModal.vue`)**: Real-time completion percentage indicator (`[ 📊 {percentage}% Mastered ]`) embedded in the top nav HUD and stepper, alongside a dedicated modal displaying overall mastery gauges and a topic-by-topic breakdown checklist with quick-focus camera buttons.
5. **Differentiated Modes for Research Papers vs. College Study Materials**:
   - **Research Mode**: Focuses on theoretical novelty ($O(1)$ parallel operations vs. $O(N)$ recurrence), formal equations ($\text{MultiHead}(Q,K,V)$), empirical ablation study benchmarks, and active BibTeX citation generator with one-click copy.
   - **Study Mode**: Syllabus mastery tracking, real-world analogies, executable C kernel system calls (`fork()`, `execvp()`), and high-yield professor exam trap warnings.
6. **Interactive Gamified Quiz Master & Personal Notes**: Take instant 4-choice multiple-choice quizzes with explanations (+25 XP), and write, persist, and export personal notes for individual topics or the entire document to Markdown (`.md`).
7. **Realistic End-to-End Walkthrough Video (`DemoVideoModal.vue`)**: 7-chapter guided in-browser walkthrough directly embedding the live 3D Three.js canvas, highlighting how Regulus AI gives intelligent replies after document ingestion, narrated with a soothing female voice.
8. **Soothing Bluish Theme Harmonization & Interactive Sparkles**: Seamless synchronization between Dark Mode (Midnight Slate-Navy) and Light Mode (Frost Blue) across all components with strict solid color blocking (zero gradients) and an interactive 60fps cursor sparkle trail.
