from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.db.session import engine, Base
from app.models.repository import Repository  # noqa: F401 — needed for table creation
from app.search.router import router as search_router
from app.repository.router import router as repository_router
from app.github.client import github_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown: close GitHub client
    await github_client.close()


app = FastAPI(
    title="RepoLens API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(search_router)
app.include_router(repository_router)


@app.get("/")
def root():
    return {"message": "RepoLens API Running 🚀"}
