"""
Hybrid Search Module — Reciprocal Rank Fusion (RRF)

Merges keyword-based search results (BM25-style) with vector similarity
results (Qdrant embeddings) using Reciprocal Rank Fusion scoring.

RRF Formula:  score(d) = Σ  1 / (k + rank_i(d))
              where k = 60 (constant), i = each result set

This approach is model-agnostic and produces significantly better relevance
than either keyword or vector search alone. A query like "distributed backend
in Go" will surface repos that don't explicitly contain those words but are
semantically similar.
"""

import logging
from typing import Optional
from app.search.schemas import RepositoryDTO

logger = logging.getLogger(__name__)

# RRF constant — higher values give more weight to lower-ranked results
RRF_K = 60


def reciprocal_rank_fusion(
    keyword_results: list[dict],
    vector_results: list[dict],
    k: int = RRF_K,
    limit: int = 20,
) -> list[dict]:
    """
    Merge two ranked lists using Reciprocal Rank Fusion.

    Each result dict must have a 'github_id' key for deduplication.
    Returns a combined, re-ranked list sorted by fused score.
    """
    fused_scores: dict[str, float] = {}
    result_map: dict[str, dict] = {}

    # Score keyword results
    for rank, item in enumerate(keyword_results, start=1):
        repo_id = str(item.get("github_id", item.get("id", "")))
        if not repo_id:
            continue
        fused_scores[repo_id] = fused_scores.get(repo_id, 0.0) + 1.0 / (k + rank)
        result_map[repo_id] = item

    # Score vector results
    for rank, item in enumerate(vector_results, start=1):
        repo_id = str(item.get("github_id", item.get("id", "")))
        if not repo_id:
            continue
        fused_scores[repo_id] = fused_scores.get(repo_id, 0.0) + 1.0 / (k + rank)
        # Prefer keyword result data if already present (it's richer)
        if repo_id not in result_map:
            result_map[repo_id] = item

    # Sort by fused score descending
    ranked_ids = sorted(fused_scores.keys(), key=lambda x: fused_scores[x], reverse=True)

    results = []
    for repo_id in ranked_ids[:limit]:
        item = result_map[repo_id]
        item["rrf_score"] = round(fused_scores[repo_id], 6)
        results.append(item)

    logger.info(
        f"RRF fusion: {len(keyword_results)} keyword + {len(vector_results)} vector → {len(results)} merged"
    )
    return results


async def hybrid_search(
    query: str,
    keyword_fn,
    vector_fn,
    limit: int = 20,
) -> list[dict]:
    """
    Run keyword and vector searches in parallel, then fuse with RRF.

    Args:
        query: The user's search string
        keyword_fn: Async callable returning list[dict] of keyword results
        vector_fn: Async callable returning list[dict] of vector results
        limit: Max results to return

    Returns:
        Fused, re-ranked list of repository dicts
    """
    import asyncio

    keyword_task = asyncio.create_task(keyword_fn(query))
    vector_task = asyncio.create_task(vector_fn(query))

    keyword_results, vector_results = await asyncio.gather(
        keyword_task, vector_task, return_exceptions=True
    )

    # Handle failures gracefully — fall back to whichever succeeded
    if isinstance(keyword_results, Exception):
        logger.warning(f"Keyword search failed: {keyword_results}")
        keyword_results = []
    if isinstance(vector_results, Exception):
        logger.warning(f"Vector search failed: {vector_results}")
        vector_results = []

    if not keyword_results and not vector_results:
        return []

    return reciprocal_rank_fusion(keyword_results, vector_results, limit=limit)
