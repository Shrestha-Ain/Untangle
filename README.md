# Untangle — Research Realm GraphRAG Explorer

A from-scratch implementation of Microsoft's GraphRAG architecture, wrapped in a gamified **"Research Realm"** UI. Upload academic papers, watch them get transformed into an isometric knowledge town, and explore entity relationships through an RPG-style quest interface.

**Stack:** Vue 3 · TypeScript · Vite · Tailwind CSS · FastAPI · Neo4j · PostgreSQL · Qdrant · Redis · Celery

---

## Prerequisites

Make sure you have these installed before anything else:

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

OR

pip install uv

# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## Backend Setup (FastAPI + uv)

```bash
# 1. Navigate to the backend folder
cd backend

# 2. Create the virtual environment using the pinned Python version
uv venv

# 3. Install all dependencies from the lockfile (exact versions, fast)
uv sync

# 4. Copy the env template and fill in your secrets
cp .env.example .env
```

Open `.env` and set the required values:

```env
# Database connections
DATABASE_URL=postgresql://user:password@localhost:5432/untangle
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
QDRANT_URL=http://localhost:6333

# Redis / Celery
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key-here          # generate with: openssl rand -hex 32
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# LLM API (use at least one)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

```bash
# 5. Run the development server (auto-reloads on file changes)
uv run uvicorn app.main:app --reload --port 8000

# 6. (Separate terminal) Run the Celery worker for async ingestion jobs
uv run celery -A app.core.celery_app worker --loglevel=info
```

API will be live at **http://localhost:8000**  
Interactive docs at **http://localhost:8000/docs**

> **Dev tip:** You never need to activate the virtual environment manually.
> `uv run <command>` always uses the project's `.venv` automatically.

---

## Frontend Setup (Vue 3 + Vite + Tailwind)

```bash
# 1. Navigate to the frontend folder
cd frontend

# 2. Install all dependencies from package-lock.json
npm install

# 3. Copy the env template
cp .env.example .env.local
```

Open `frontend/.env.local` and set:

```env
# Points the Axios client at your local FastAPI server
VITE_API_URL=http://localhost:8000
```

```bash
# 4. Start the dev server (hot-reloads on file changes)
npm run dev
```

Frontend will be live at **http://localhost:5173**

> **How the proxy works:** In development, the Vite dev server proxies any
> request to `/api/*` → `http://localhost:8000` and `/ws/*` → `ws://localhost:8000`.
> This means you never hit CORS issues locally — the browser only ever talks to port 5173.

---

## Running Both Together

Open **two terminals** side by side:

```bash
# Terminal 1 — Backend
cd backend
uv run uvicorn app.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
npm run dev
```

Then open **http://localhost:5173** in your browser.

---

## Other Useful Commands

### Backend

```bash
# Run tests
uv run pytest

# Lint & format
uv run ruff check .
uv run ruff format .

# Add a new dependency
uv add <package-name>

# Add a dev-only dependency
uv add --dev <package-name>
```

### Frontend

```bash
# Type-check without building
npm run type-check

# Build for production
npm run build

# Preview the production build locally
npm run preview
```