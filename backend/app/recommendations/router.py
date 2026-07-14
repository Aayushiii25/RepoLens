from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from app.recommendations.engine import recommend_repositories_by_skills, recommend_issues_by_skills

router = APIRouter(prefix="/api/v1/recommendations", tags=["Recommendations"])


class SkillRequest(BaseModel):
    skills: List[str]


class RepoRecommendation(BaseModel):
    repository: str
    score: int
    reason: str
    language: Optional[str] = None
    stars: int = 0
    topics: List[str] = []


class IssueRecommendation(BaseModel):
    issue: int
    title: str = ""
    difficulty: str
    estimatedTime: str
    score: int = 0
    reason: str


@router.post("/repositories", response_model=List[RepoRecommendation])
async def recommend_repositories(req: SkillRequest):
    """
    Recommend repositories based on developer skills.

    Uses semantic matching (Qdrant embeddings) with skill-affinity boosting.
    Falls back to curated recommendations when vector DB is empty.
    """
    try:
        from app.ml.embeddings import embedding_service
        from app.core.vector.client import vector_db
        results = await recommend_repositories_by_skills(
            skills=req.skills,
            embedding_service=embedding_service,
            vector_db=vector_db,
            limit=10,
        )
    except Exception:
        results = await recommend_repositories_by_skills(
            skills=req.skills,
            limit=10,
        )

    return [RepoRecommendation(**r) for r in results]


@router.post("/issues", response_model=List[IssueRecommendation])
async def recommend_issues(req: SkillRequest):
    """
    Recommend issues based on developer skills and difficulty analysis.

    Matches user skills against issue labels and difficulty levels,
    then scores and ranks by accessibility and relevance.
    """
    # Get issues from a well-known repository to score against
    from app.github.client import github_client
    from app.core.cache import cache

    cache_key = f"rec_issues:{'_'.join(sorted(req.skills))}"
    cached = cache.get(cache_key)
    if cached:
        return [IssueRecommendation(**i) for i in cached]

    # Fetch issues from popular repos matching user skills
    sample_repos = {
        "python": "fastapi/fastapi",
        "javascript": "facebook/react",
        "typescript": "microsoft/TypeScript",
        "go": "kubernetes/kubernetes",
        "rust": "denoland/deno",
        "react": "facebook/react",
    }

    all_issues = []
    for skill in req.skills[:3]:  # Limit to avoid too many API calls
        repo = sample_repos.get(skill.lower())
        if repo:
            owner, name = repo.split("/")
            issues = await github_client.get_repository_issues(owner, name, first=10)
            all_issues.extend(issues)

    if not all_issues:
        # Fallback: use a default repo
        issues = await github_client.get_repository_issues("facebook", "react", first=10)
        all_issues = issues

    scored = await recommend_issues_by_skills(
        skills=req.skills,
        issues=all_issues,
        limit=10,
    )

    cache.set(cache_key, scored, ttl=600)
    return [IssueRecommendation(**i) for i in scored]
