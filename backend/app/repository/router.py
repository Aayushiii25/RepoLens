from fastapi import APIRouter, HTTPException
from app.github.client import github_client
from app.core.cache import cache
from app.repository.schemas import RepositoryDetailDTO, IssueDTO, CommitDTO
from app.ml.llm import llm_gateway
from app.repository.health import calculate_detailed_health

router = APIRouter(prefix="/api/v1/repositories", tags=["Repositories"])


@router.get("/{owner}/{name}", response_model=RepositoryDetailDTO)
async def get_repository(owner: str, name: str):
    """Get full repository details including health scores, languages, and contributors."""
    cache_key = f"repo:{owner}/{name}"
    cached = cache.get(cache_key)
    if cached:
        return RepositoryDetailDTO(**cached)

    result = await github_client.get_repository(owner, name)
    if not result:
        raise HTTPException(status_code=404, detail="Repository not found")

    cache.set(cache_key, result, ttl=300)
    return RepositoryDetailDTO(**result)


@router.get("/{owner}/{name}/health")
async def get_repository_health(owner: str, name: str):
    """
    Get detailed health score breakdown for a repository.

    Returns overall score plus per-dimension scores (activity, community,
    documentation, security, maintainability) with trend indicators,
    factor details, and actionable recommendations.
    """
    cache_key = f"health:{owner}/{name}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    # Get repository data
    repo_data = await github_client.get_repository(owner, name)
    if not repo_data:
        raise HTTPException(status_code=404, detail="Repository not found")

    # Calculate detailed health
    health = calculate_detailed_health(repo_data)

    cache.set(cache_key, health, ttl=600)  # 10 min cache for health data
    return health


@router.get("/{owner}/{name}/issues", response_model=list[IssueDTO])
async def get_repository_issues(owner: str, name: str):
    """Get open issues for a repository with difficulty labels."""
    cache_key = f"issues:{owner}/{name}"
    cached = cache.get(cache_key)
    if cached:
        return [IssueDTO(**i) for i in cached]

    result = await github_client.get_repository_issues(owner, name)
    cache.set(cache_key, result, ttl=300)
    return [IssueDTO(**i) for i in result]


@router.get("/{owner}/{name}/activity", response_model=list[CommitDTO])
async def get_repository_activity(owner: str, name: str):
    """Get recent commit activity for a repository."""
    cache_key = f"activity:{owner}/{name}"
    cached = cache.get(cache_key)
    if cached:
        return [CommitDTO(**c) for c in cached]

    result = await github_client.get_repository_activity(owner, name)
    cache.set(cache_key, result, ttl=300)
    return [CommitDTO(**c) for c in result]


@router.get("/{owner}/{name}/summary")
async def get_repository_summary(owner: str, name: str):
    """Generate an AI-powered summary of the repository."""
    cache_key = f"summary:{owner}/{name}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    # Get repository details first
    repo_data = await github_client.get_repository(owner, name)
    if not repo_data:
        raise HTTPException(status_code=404, detail="Repository not found")

    # Generate summary
    summary = await llm_gateway.generate_repository_summary(repo_data)

    cache.set(cache_key, summary, ttl=86400)  # Cache for 24 hours
    return summary


@router.get("/{owner}/{name}/similar")
async def get_similar_repositories(owner: str, name: str, limit: int = 5):
    """
    Find repositories similar to the given one using vector similarity.

    Generates an embedding from the repository's description + topics + language,
    then queries Qdrant for the nearest neighbors.
    """
    cache_key = f"similar:{owner}/{name}:{limit}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    # Get repository data
    repo_data = await github_client.get_repository(owner, name)
    if not repo_data:
        raise HTTPException(status_code=404, detail="Repository not found")

    try:
        from app.ml.embeddings import embedding_service
        from app.core.vector.client import vector_db

        # Build embedding text
        parts = []
        if repo_data.get("description"):
            parts.append(repo_data["description"])
        if repo_data.get("topics"):
            parts.append(" ".join(repo_data["topics"]))
        if repo_data.get("language"):
            parts.append(repo_data["language"])

        text = " ".join(parts)
        if not text.strip():
            return {"similar": [], "count": 0}

        vector = embedding_service.encode(text)
        hits = await vector_db.search(vector, limit=limit + 1)  # +1 to exclude self

        similar = []
        for hit in hits:
            payload = hit.get("payload", {})
            # Skip self
            if payload.get("full_name") == f"{owner}/{name}":
                continue
            similar.append({
                "full_name": payload.get("full_name", ""),
                "description": payload.get("description", ""),
                "language": payload.get("language"),
                "stars": payload.get("stars", 0),
                "topics": payload.get("topics", []),
                "similarity_score": round(hit.get("score", 0), 4),
            })

        result = {"similar": similar[:limit], "count": len(similar[:limit])}
        cache.set(cache_key, result, ttl=600)
        return result
    except Exception as e:
        return {"similar": [], "count": 0, "error": str(e)}
