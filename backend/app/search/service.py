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
      4. Generate embeddings and store in Qdrant (async, non-blocking)
      5. Store in cache with TTL
      6. Return results
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

    # 4. Store embeddings in Qdrant (best-effort, non-blocking)
    await _index_embeddings(raw_results)

    # 5. Cache the results
    cache.set(cache_key, [dto.model_dump() for dto in dtos], ttl=settings.CACHE_TTL)

    return dtos, False


async def _index_embeddings(results: list[dict]) -> None:
    """
    Generate embeddings for search results and upsert into Qdrant.
    Runs best-effort — failures are logged but don't break search.
    """
    try:
        from app.ml.embeddings import embedding_service
        from app.core.vector.client import vector_db

        for item in results:
            # Build text for embedding: description + topics + language
            parts = []
            if item.get("description"):
                parts.append(item["description"])
            if item.get("topics"):
                parts.append(" ".join(item["topics"]))
            if item.get("language"):
                parts.append(item["language"])
            if item.get("full_name"):
                parts.append(item["full_name"])

            text = " ".join(parts)
            if not text.strip():
                continue

            vector = embedding_service.encode(text)
            repo_id = item.get("github_id", "")
            if not repo_id:
                continue

            # Use hash of github_id as integer ID for Qdrant
            point_id = abs(hash(repo_id)) % (2**63)

            payload = {
                "github_id": repo_id,
                "full_name": item.get("full_name", ""),
                "name": item.get("name", ""),
                "owner": item.get("owner", ""),
                "description": item.get("description", ""),
                "language": item.get("language"),
                "stars": item.get("stars", 0),
                "forks": item.get("forks", 0),
                "topics": item.get("topics", []),
            }

            await vector_db.upsert_repository(point_id, vector, payload)

        logger.info(f"Indexed {len(results)} repositories into Qdrant")
    except Exception as e:
        logger.warning(f"Embedding indexing failed (non-fatal): {e}")


async def keyword_search_db(query: str, db: Session = None) -> list[dict]:
    """
    Search the local SQLite database for keyword matches.
    Used as the keyword leg of hybrid search.
    """
    try:
        from app.db.session import SessionLocal
        if db is None:
            db = SessionLocal()
            close_after = True
        else:
            close_after = False

        results = (
            db.query(Repository)
            .filter(
                Repository.full_name.ilike(f"%{query}%")
                | Repository.description.ilike(f"%{query}%")
            )
            .order_by(Repository.stars.desc())
            .limit(20)
            .all()
        )

        items = []
        for r in results:
            items.append({
                "github_id": r.github_id,
                "full_name": r.full_name,
                "owner": r.owner,
                "name": r.name,
                "description": r.description,
                "language": r.language,
                "stars": r.stars,
                "forks": r.forks,
                "open_issues": r.open_issues,
                "topics": r.topics or [],
                "license": r.license,
            })

        if close_after:
            db.close()

        return items
    except Exception as e:
        logger.warning(f"Keyword DB search failed: {e}")
        return []
