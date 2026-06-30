from fastapi import APIRouter, HTTPException
from app.github.client import github_client
from app.core.cache import cache
from app.repository.schemas import RepositoryDetailDTO, IssueDTO, CommitDTO
from app.ml.llm import llm_gateway

router = APIRouter(prefix="/api/v1/repositories", tags=["Repositories"])


@router.get("/{owner}/{name}", response_model=RepositoryDetailDTO)
async def get_repository(owner: str, name: str):
    cache_key = f"repo:{owner}/{name}"
    cached = cache.get(cache_key)
    if cached:
        return RepositoryDetailDTO(**cached)

    result = await github_client.get_repository(owner, name)
    if not result:
        raise HTTPException(status_code=404, detail="Repository not found")

    cache.set(cache_key, result, ttl=300)
    return RepositoryDetailDTO(**result)


@router.get("/{owner}/{name}/issues", response_model=list[IssueDTO])
async def get_repository_issues(owner: str, name: str):
    cache_key = f"issues:{owner}/{name}"
    cached = cache.get(cache_key)
    if cached:
        return [IssueDTO(**i) for i in cached]

    result = await github_client.get_repository_issues(owner, name)
    cache.set(cache_key, result, ttl=300)
    return [IssueDTO(**i) for i in result]


@router.get("/{owner}/{name}/activity", response_model=list[CommitDTO])
async def get_repository_activity(owner: str, name: str):
    cache_key = f"activity:{owner}/{name}"
    cached = cache.get(cache_key)
    if cached:
        return [CommitDTO(**c) for c in cached]

    result = await github_client.get_repository_activity(owner, name)
    cache.set(cache_key, result, ttl=300)
    return [CommitDTO(**c) for c in result]


@router.get("/{owner}/{name}/summary")
async def get_repository_summary(owner: str, name: str):
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
    
    cache.set(cache_key, summary, ttl=86400) # Cache for 24 hours
    return summary

