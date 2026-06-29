import json
import logging
from sqlalchemy.orm import Session
from app.github.client import github_client
from app.core.cache import cache
from app.core.config import get_settings
from app.models.repository import Repository
from app.search.schemas import RepositoryDTO

logger = logging.getLogger(__name__)
settings = get_settings()


async def search_repositories(query: str, db: Session) -> tuple[list[RepositoryDTO], bool]:
    """
    Search repositories with cache-first strategy.
    Returns (results, was_cached).

    Flow:
      1. Check in-memory cache → return if hit
      2. Call GitHub GraphQL API
      3. Upsert results into SQLite
      4. Store in cache with TTL
      5. Return results
    """
    if not query or not query.strip():
        return [], False

    cache_key = f"search:{query.lower().strip()}"

    # 1. Cache check
    cached = cache.get(cache_key)
    if cached is not None:
        logger.info(f"Cache HIT for query: {query}")
        return [RepositoryDTO(**item) for item in cached], True

    # 2. Call GitHub
    logger.info(f"Cache MISS for query: {query} — calling GitHub")
    raw_results = await github_client.search_repositories(query)

    if not raw_results:
        # Even empty results get cached briefly to prevent hammering GitHub
        cache.set(cache_key, [], ttl=60)
        return [], False

    # 3. Upsert into database
    dtos: list[RepositoryDTO] = []
    for item in raw_results:
        existing = db.query(Repository).filter_by(github_id=item["github_id"]).first()
        if existing:
            for key, value in item.items():
                setattr(existing, key, value)
            db.flush()
            dtos.append(RepositoryDTO.model_validate(existing))
        else:
            repo = Repository(**item)
            db.add(repo)
            db.flush()
            dtos.append(RepositoryDTO.model_validate(repo))

    db.commit()

    # 4. Cache the results
    cache.set(cache_key, [dto.model_dump() for dto in dtos], ttl=settings.CACHE_TTL)

    return dtos, False
