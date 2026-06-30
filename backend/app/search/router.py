from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.search.schemas import SearchResponse
from app.search import service
from pydantic import BaseModel
from app.ml.embeddings import embedding_service
from app.core.vector.client import vector_db

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
    """Search repositories using natural language and Qdrant."""
    try:
        # Generate embedding
        vector = embedding_service.encode(request.query)
        
        # Search Qdrant
        results = await vector_db.search(vector, limit=request.limit)
        
        return {
            "query": request.query,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Semantic search failed: {str(e)}")
