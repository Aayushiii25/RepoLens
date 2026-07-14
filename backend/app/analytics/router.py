from fastapi import APIRouter
from app.core.cache import cache
from app.github.client import github_client
from sqlalchemy import func
from app.db.session import SessionLocal
from app.models.repository import Repository

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


@router.get("/trending")
async def trending_repositories(limit: int = 10):
    """
    Get trending repositories — sorted by star count from the local database.

    In production this would query GitHub's trending API or calculate
    star velocity over time. For now, returns repositories with highest
    stars from the local cache, representing the most popular repos
    the user has searched for.
    """
    cache_key = f"trending:{limit}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    db = SessionLocal()
    try:
        repos = (
            db.query(Repository)
            .order_by(Repository.stars.desc())
            .limit(limit)
            .all()
        )

        results = []
        for repo in repos:
            results.append({
                "full_name": repo.full_name,
                "owner": repo.owner,
                "name": repo.name,
                "description": repo.description,
                "language": repo.language,
                "stars": repo.stars,
                "forks": repo.forks,
                "topics": repo.topics or [],
                "updated_at": repo.updated_at,
            })

        # If no local data yet, return curated trending
        if not results:
            results = [
                {"full_name": "vercel/next.js", "stars": 133000, "language": "JavaScript",
                 "description": "The React Framework", "forks": 28000, "topics": ["react", "nextjs"]},
                {"full_name": "facebook/react", "stars": 232000, "language": "JavaScript",
                 "description": "The library for web and native user interfaces", "forks": 47000, "topics": ["react", "ui"]},
                {"full_name": "microsoft/TypeScript", "stars": 105000, "language": "TypeScript",
                 "description": "TypeScript is a superset of JavaScript", "forks": 12500, "topics": ["typescript"]},
                {"full_name": "fastapi/fastapi", "stars": 82000, "language": "Python",
                 "description": "High performance Python web framework", "forks": 7000, "topics": ["python", "api"]},
                {"full_name": "kubernetes/kubernetes", "stars": 115000, "language": "Go",
                 "description": "Production-Grade Container Scheduling and Management", "forks": 40000, "topics": ["kubernetes", "containers"]},
            ]

        cache.set(cache_key, results, ttl=300)
        return results
    finally:
        db.close()


@router.get("/languages")
async def language_trends():
    """
    Get programming language distribution across stored repositories.

    Aggregates language data from all repositories in the local database,
    providing a real-time view of language popularity within the user's
    search history.
    """
    cache_key = "language_trends"
    cached = cache.get(cache_key)
    if cached:
        return cached

    db = SessionLocal()
    try:
        results = (
            db.query(
                Repository.language,
                func.count(Repository.id).label("count"),
                func.sum(Repository.stars).label("total_stars"),
            )
            .filter(Repository.language.isnot(None))
            .group_by(Repository.language)
            .order_by(func.count(Repository.id).desc())
            .limit(15)
            .all()
        )

        total_repos = sum(r.count for r in results) if results else 1
        language_data = []
        for r in results:
            language_data.append({
                "language": r.language,
                "count": r.count,
                "percentage": round((r.count / total_repos) * 100, 1),
                "total_stars": r.total_stars or 0,
            })

        # Fallback if database is empty
        if not language_data:
            language_data = [
                {"language": "TypeScript", "count": 0, "percentage": 28.5, "total_stars": 0},
                {"language": "Python", "count": 0, "percentage": 22.1, "total_stars": 0},
                {"language": "JavaScript", "count": 0, "percentage": 18.3, "total_stars": 0},
                {"language": "Go", "count": 0, "percentage": 12.7, "total_stars": 0},
                {"language": "Rust", "count": 0, "percentage": 8.9, "total_stars": 0},
                {"language": "Java", "count": 0, "percentage": 5.2, "total_stars": 0},
            ]

        cache.set(cache_key, language_data, ttl=300)
        return language_data
    finally:
        db.close()


@router.get("/topics")
async def technology_trends():
    """
    Get topic/technology trends from stored repositories.

    Aggregates topic tags from repository metadata to show which
    technologies are most represented in the user's searches.
    """
    cache_key = "topic_trends"
    cached = cache.get(cache_key)
    if cached:
        return cached

    db = SessionLocal()
    try:
        repos = db.query(Repository).all()

        topic_counts: dict[str, int] = {}
        topic_stars: dict[str, int] = {}
        for repo in repos:
            topics = repo.topics or []
            for topic in topics:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
                topic_stars[topic] = topic_stars.get(topic, 0) + (repo.stars or 0)

        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:20]

        topic_data = [
            {
                "topic": topic,
                "count": count,
                "total_stars": topic_stars.get(topic, 0),
            }
            for topic, count in sorted_topics
        ]

        # Fallback if database is empty
        if not topic_data:
            topic_data = [
                {"topic": "machine-learning", "count": 0, "total_stars": 0},
                {"topic": "react", "count": 0, "total_stars": 0},
                {"topic": "kubernetes", "count": 0, "total_stars": 0},
                {"topic": "api", "count": 0, "total_stars": 0},
                {"topic": "typescript", "count": 0, "total_stars": 0},
            ]

        cache.set(cache_key, topic_data, ttl=300)
        return topic_data
    finally:
        db.close()
