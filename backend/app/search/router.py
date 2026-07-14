from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.search.schemas import SearchResponse
from app.search import service
from pydantic import BaseModel
from app.search.hybrid import hybrid_search, reciprocal_rank_fusion

router = APIRouter(prefix="/api/v1", tags=["Search"])


@router.get("/search", response_model=SearchResponse)
async def search_repositories(
    q: str = Query(..., min_length=1, description="Search query"),
    db: Session = Depends(get_db),
):
    """Search GitHub repositories with caching."""
    try:
        results, cached = await service.search_repositories(q, db)
        return SearchResponse(
            query=q,
            count=len(results),
            results=results,
            cached=cached,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


class SemanticSearchRequest(BaseModel):
    query: str
    limit: int = 10


@router.post("/search/semantic")
async def semantic_search(request: SemanticSearchRequest):
    """
    Search repositories using natural language and hybrid RRF scoring.

    Pipeline:
      1. Encode query → embedding vector
      2. Run vector search (Qdrant) in parallel with keyword search (SQLite)
      3. Fuse results using Reciprocal Rank Fusion (RRF)
      4. Return re-ranked results
    """
    try:
        from app.ml.embeddings import embedding_service
        from app.core.vector.client import vector_db

        # Vector search function
        async def vector_search(q: str) -> list[dict]:
            vec = embedding_service.encode(q)
            hits = await vector_db.search(vec, limit=request.limit * 2)
            return [
                {
                    "github_id": h["payload"].get("github_id", ""),
                    "full_name": h["payload"].get("full_name", ""),
                    "owner": h["payload"].get("owner", ""),
                    "name": h["payload"].get("name", ""),
                    "description": h["payload"].get("description", ""),
                    "language": h["payload"].get("language"),
                    "stars": h["payload"].get("stars", 0),
                    "forks": h["payload"].get("forks", 0),
                    "topics": h["payload"].get("topics", []),
                    "vector_score": round(h.get("score", 0), 4),
                }
                for h in hits
            ]

        # Keyword search function
        async def keyword_search(q: str) -> list[dict]:
            return await service.keyword_search_db(q)

        # Hybrid fusion
        fused_results = await hybrid_search(
            query=request.query,
            keyword_fn=keyword_search,
            vector_fn=vector_search,
            limit=request.limit,
        )

        return {
            "query": request.query,
            "count": len(fused_results),
            "search_type": "hybrid_rrf",
            "results": fused_results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Semantic search failed: {str(e)}")
