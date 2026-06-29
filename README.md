<p align="center">
  <h1 align="center">🔍 RepoLens</h1>
  <p align="center">
    <strong>AI-Powered Open Source Discovery & Contribution Intelligence Platform</strong>
  </p>
  <p align="center">
    <a href="#architecture">Architecture</a> •
    <a href="#features">Features</a> •
    <a href="#tech-stack">Tech Stack</a> •
    <a href="#getting-started">Getting Started</a> •
    <a href="#project-structure">Project Structure</a>
  </p>
</p>

---

## 💡 What is RepoLens?

**RepoLens** is a full-stack platform that helps developers discover high-quality open-source repositories, evaluate repository health, and find meaningful contribution opportunities — powered by the GitHub GraphQL API and a cache-first backend architecture.

> Traditional GitHub search is keyword-only. RepoLens goes further — providing repository health scores, tech stack analysis, recommended issues by difficulty, and AI-powered summaries in a single, beautiful interface.

---

## 🏗️ Architecture

<a name="architecture"></a>

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js)                       │
│  Command Palette (⌘K) → Search Results → Repository Workspace  │
└──────────────────────────────┬──────────────────────────────────┘
                               │ HTTP (REST)
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                        BACKEND (FastAPI)                        │
│                                                                 │
│  ┌──────────┐   ┌──────────────┐   ┌─────────────────────────┐ │
│  │  Router   │──▶│   Service    │──▶│    GitHub GraphQL API   │ │
│  │ /api/v1/  │   │ (Cache-First)│   │  (Authenticated, Async) │ │
│  └──────────┘   └──────┬───────┘   └─────────────────────────┘ │
│                         │                                       │
│              ┌──────────┼──────────┐                            │
│              ▼                     ▼                            │
│     ┌──────────────┐     ┌──────────────┐                      │
│     │  TTL Cache    │     │   Database   │                      │
│     │ (In-Memory)   │     │  (SQLite)    │                      │
│     │  5-min TTL    │     │  Upsert-on-  │                      │
│     │               │     │  write       │                      │
│     └──────────────┘     └──────────────┘                      │
└─────────────────────────────────────────────────────────────────┘
```

**Key architectural decisions:**
- **Cache-first reads**: Search results are served from cache on subsequent requests (<50ms vs ~1s from GitHub)
- **Upsert-on-write**: Every GitHub response is persisted to the database, building a local knowledge base over time
- **Async I/O**: The GitHub client uses `httpx.AsyncClient` for non-blocking HTTP requests
- **Clean separation**: The frontend never sees raw GitHub API responses — data is transformed by the service layer

---

## ✨ Features

<a name="features"></a>

### Implemented
| Feature | Description |
|---|---|
| 🔎 **Live GitHub Search** | Real-time repository search via GitHub GraphQL API with debounced input |
| ⚡ **Command Palette** | `Ctrl+K` / `⌘K` powered search with keyboard navigation (arrow keys, Enter, Esc) |
| 🏥 **Repository Health Score** | Visual health metrics: Activity, Security, Community, Documentation, Maintainability |
| 🧱 **Tech Stack Detection** | Auto-detected technology badges for each repository |
| 📊 **Recommended Issues** | Issue table with difficulty rating, estimated time, and acceptance rate |
| 🕐 **Recent & Trending Searches** | Persisted search history (localStorage) + curated trending terms |
| 🎨 **Dual Theme** | Dark mode with golden glow, light mode with blood-red aesthetic — fully responsive |
| 💀 **Skeleton Loading** | Animated skeleton states — never a spinner, never a frozen page |
| 🏛️ **3-Column Layout** | GitHub + Linear + VS Code inspired workspace with sticky sidebar |

### Planned
- 🤖 AI-powered repository summaries (LLM integration)
- 🧠 Semantic search via embeddings (Qdrant + Sentence Transformers)
- 📈 Analytics dashboard (star trends, contributor growth)
- 🔐 GitHub OAuth authentication
- 🐳 Docker Compose for Postgres + Redis production setup

---

## 🛠️ Tech Stack

<a name="tech-stack"></a>

### Frontend
| Technology | Purpose |
|---|---|
| **Next.js 15** | React framework with App Router |
| **TypeScript** | Type-safe development |
| **Tailwind CSS** | Utility-first styling |
| **shadcn/ui** | Headless UI component library |
| **cmdk** | Command palette (keyboard-first search) |
| **next-themes** | Dark/light mode support |

### Backend
| Technology | Purpose |
|---|---|
| **FastAPI** | Async Python web framework |
| **SQLAlchemy** | ORM with SQLite (swappable to PostgreSQL) |
| **httpx** | Async HTTP client for GitHub API |
| **Pydantic v2** | Request/response validation & serialization |
| **In-Memory Cache** | TTL-based caching (Redis-compatible interface) |

### APIs
| API | Purpose |
|---|---|
| **GitHub GraphQL API** | Repository search, metadata, and issue data |

---

## 🚀 Getting Started

<a name="getting-started"></a>

### Prerequisites
- **Node.js** ≥ 18
- **Python** ≥ 3.11
- **GitHub Personal Access Token** ([Generate here](https://github.com/settings/tokens) — Classic, `public_repo` scope)

### 1. Clone the repository

```bash
git clone https://github.com/Aayushiii25/RepoLens.git
cd RepoLens
```

### 2. Start the Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
pip install -r requirements.txt

# Configure your GitHub token
echo "GITHUB_TOKEN=ghp_your_token_here" > .env
echo "DATABASE_URL=sqlite:///./repolens.db" >> .env

# Run the server
uvicorn app.main:app --reload --port 8000
```

📄 Swagger docs available at [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

🌐 App available at [http://localhost:3002](http://localhost:3002)

---

## 📁 Project Structure

<a name="project-structure"></a>

```
RepoLens/
├── frontend/                    # Next.js 15 application
│   ├── src/
│   │   ├── app/                 # App Router (route groups)
│   │   ├── components/          # Shared UI (Navbar, AppShell, shadcn)
│   │   ├── features/            # Feature modules
│   │   │   ├── repository/      #   Repository workspace components
│   │   │   └── search/          #   Search & command palette
│   │   ├── services/            # API client layer
│   │   └── data/                # Static data (trending searches)
│   └── package.json
│
├── backend/                     # FastAPI application
│   ├── app/
│   │   ├── core/                # Config, cache
│   │   ├── db/                  # SQLAlchemy session & engine
│   │   ├── github/              # GitHub GraphQL client
│   │   ├── models/              # Database models
│   │   ├── search/              # Search router, service, schemas
│   │   └── main.py              # FastAPI entrypoint
│   ├── docker/                  # Docker Compose (Postgres + Redis)
│   ├── requirements.txt
│   └── .env                     # Environment variables
│
└── README.md
```

---

## 📡 API Reference

### `GET /api/v1/search?q={query}`

Search GitHub repositories with caching.

**Response:**
```json
{
  "query": "react",
  "count": 20,
  "cached": false,
  "results": [
    {
      "id": 1,
      "full_name": "facebook/react",
      "owner": "facebook",
      "name": "react",
      "description": "The library for web and native user interfaces.",
      "language": "JavaScript",
      "stars": 232000,
      "forks": 47400,
      "open_issues": 940,
      "topics": ["javascript", "frontend", "react"],
      "license": "MIT",
      "updated_at": "2026-06-29T10:00:00Z"
    }
  ]
}
```

---

## 🧠 Engineering Highlights

- **Cache-First Architecture**: First request hits GitHub (~1s). Subsequent identical searches are served from the in-memory TTL cache (<50ms). All results are persisted to the database for long-term storage.
- **GraphQL over REST**: Uses GitHub's GraphQL API to fetch exactly the fields needed in a single request — no over-fetching.
- **Debounced Search**: The frontend waits 400ms after the user stops typing before making an API call, preventing unnecessary requests.
- **Clean DTO Pattern**: Raw GitHub GraphQL responses are never exposed to the frontend. The service layer transforms them into typed Pydantic models.
- **Upsert Strategy**: Database writes use an "update if exists, insert if new" pattern to avoid duplicate records while keeping data fresh.

---

## 👤 Author

**Aayushi Dhurandhar**

- GitHub: [@Aayushiii25](https://github.com/Aayushiii25)

---

<p align="center">
  Built with ❤️ using Next.js, FastAPI, and the GitHub GraphQL API
</p>
