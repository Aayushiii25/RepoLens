"""
Recommendation Engine

Provides skill-based repository recommendations and issue recommendations
using a combination of:
  1. Semantic matching (embed user skills → search Qdrant)
  2. Skill-affinity scoring (language/topic matching)
  3. Issue difficulty analysis (label-based scoring)
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Skill → related topics/languages mapping for affinity scoring
SKILL_AFFINITY_MAP = {
    "python": ["django", "flask", "fastapi", "machine-learning", "data-science", "pytorch"],
    "javascript": ["react", "vue", "angular", "nodejs", "typescript", "nextjs"],
    "typescript": ["react", "angular", "nextjs", "deno", "nestjs"],
    "go": ["kubernetes", "docker", "microservices", "grpc", "cloud-native"],
    "rust": ["systems-programming", "webassembly", "cli", "performance"],
    "java": ["spring", "android", "gradle", "microservices", "enterprise"],
    "react": ["javascript", "typescript", "nextjs", "frontend", "ui"],
    "machine-learning": ["python", "tensorflow", "pytorch", "deep-learning", "nlp"],
    "devops": ["kubernetes", "docker", "terraform", "ci-cd", "aws"],
    "backend": ["api", "database", "microservices", "rest", "graphql"],
    "frontend": ["react", "vue", "css", "ui", "accessibility"],
    "data-science": ["python", "pandas", "jupyter", "visualization", "statistics"],
}

# Difficulty weights for issue scoring
DIFFICULTY_WEIGHTS = {
    "good first issue": 1.0,
    "good-first-issue": 1.0,
    "beginner": 1.0,
    "beginner-friendly": 1.0,
    "easy": 0.9,
    "documentation": 0.85,
    "docs": 0.85,
    "bug": 0.6,
    "fix": 0.6,
    "enhancement": 0.4,
    "feature": 0.3,
    "feature request": 0.3,
    "performance": 0.2,
    "security": 0.2,
}


async def recommend_repositories_by_skills(
    skills: list[str],
    embedding_service=None,
    vector_db=None,
    limit: int = 10,
) -> list[dict]:
    """
    Recommend repositories based on developer skills.

    Strategy:
      1. Encode skills as a combined text embedding
      2. Search Qdrant for semantically similar repositories
      3. Apply skill-affinity boosting
      4. Return ranked results with match reasons
    """
    results = []

    # Try vector-based search first
    if embedding_service and vector_db:
        try:
            skill_text = ", ".join(skills)
            query_text = f"Repository for developers skilled in {skill_text}"
            vector = embedding_service.encode(query_text)
            vector_results = await vector_db.search(vector, limit=limit * 2)

            for hit in vector_results:
                payload = hit.get("payload", {})
                repo_name = payload.get("full_name", payload.get("name", "Unknown"))
                base_score = int(hit.get("score", 0) * 100)

                # Apply skill-affinity boost
                repo_topics = [t.lower() for t in payload.get("topics", [])]
                repo_lang = (payload.get("language") or "").lower()
                affinity_boost = _calculate_affinity_boost(skills, repo_topics, repo_lang)

                final_score = min(99, base_score + affinity_boost)
                reason = _generate_match_reason(skills, repo_topics, repo_lang)

                results.append({
                    "repository": repo_name,
                    "score": final_score,
                    "reason": reason,
                    "language": payload.get("language"),
                    "stars": payload.get("stars", 0),
                    "topics": payload.get("topics", []),
                })
        except Exception as e:
            logger.warning(f"Vector-based recommendation failed: {e}")

    # Fallback: skill-affinity based recommendations (no vector DB needed)
    if not results:
        results = _fallback_recommendations(skills, limit)

    # Sort by score and limit
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]


async def recommend_issues_by_skills(
    skills: list[str],
    issues: list[dict],
    limit: int = 10,
) -> list[dict]:
    """
    Score and rank issues based on developer skill level.

    Strategy:
      - Match issue labels against difficulty weights
      - Boost issues that align with user's skill set
      - Estimate completion time based on difficulty
    """
    scored_issues = []

    for issue in issues:
        labels = [l.get("name", "").lower() for l in issue.get("labels", [])]
        difficulty = issue.get("difficulty", "Medium")

        # Calculate skill match score
        skill_match = 0.5  # base
        for skill in skills:
            skill_lower = skill.lower()
            for label in labels:
                if skill_lower in label or label in skill_lower:
                    skill_match = min(1.0, skill_match + 0.3)
                # Check affinity
                affinities = SKILL_AFFINITY_MAP.get(skill_lower, [])
                if label in affinities:
                    skill_match = min(1.0, skill_match + 0.15)

        # Calculate difficulty accessibility
        difficulty_score = 0.5
        for label in labels:
            if label in DIFFICULTY_WEIGHTS:
                difficulty_score = max(difficulty_score, DIFFICULTY_WEIGHTS[label])

        # Combined score
        combined_score = int((skill_match * 0.6 + difficulty_score * 0.4) * 100)

        # Estimate time
        time_estimates = {
            "Easy": "1-2 hours",
            "Medium": "3-6 hours",
            "Hard": "1-3 days",
        }
        estimated_time = time_estimates.get(difficulty, "4-8 hours")

        # Generate reason
        matching_labels = [l for l in labels if l in DIFFICULTY_WEIGHTS]
        reason = f"{'Good entry point' if difficulty_score >= 0.8 else 'Matches your profile'}"
        if matching_labels:
            reason += f" — labels: {', '.join(matching_labels[:3])}"

        scored_issues.append({
            "issue": issue.get("number", 0),
            "title": issue.get("title", ""),
            "difficulty": difficulty,
            "estimatedTime": estimated_time,
            "score": combined_score,
            "reason": reason,
        })

    scored_issues.sort(key=lambda x: x["score"], reverse=True)
    return scored_issues[:limit]


def _calculate_affinity_boost(
    skills: list[str], repo_topics: list[str], repo_language: str
) -> int:
    """Calculate a boost score based on skill-topic affinity."""
    boost = 0
    for skill in skills:
        skill_lower = skill.lower()
        # Direct language match
        if skill_lower == repo_language:
            boost += 15
        # Direct topic match
        if skill_lower in repo_topics:
            boost += 10
        # Affinity match
        affinities = SKILL_AFFINITY_MAP.get(skill_lower, [])
        for topic in repo_topics:
            if topic in affinities:
                boost += 5
        if repo_language in affinities:
            boost += 5
    return min(boost, 30)  # Cap the boost


def _generate_match_reason(
    skills: list[str], repo_topics: list[str], repo_language: str
) -> str:
    """Generate a human-readable reason for the recommendation."""
    matches = []
    for skill in skills:
        skill_lower = skill.lower()
        if skill_lower == repo_language:
            matches.append(f"uses {skill}")
        elif skill_lower in repo_topics:
            matches.append(f"tagged with {skill}")

    if matches:
        return f"Strong match — {', '.join(matches[:3])}"
    return f"Semantically similar to your skills in {', '.join(skills[:3])}"


def _fallback_recommendations(skills: list[str], limit: int) -> list[dict]:
    """Generate recommendations without vector DB, using curated mapping."""
    # Well-known repos by skill
    SKILL_REPOS = {
        "python": [
            ("fastapi/fastapi", 96, "FastAPI — modern async Python framework"),
            ("pallets/flask", 88, "Flask — lightweight Python web framework"),
            ("django/django", 85, "Django — batteries-included Python framework"),
        ],
        "javascript": [
            ("facebook/react", 95, "React — dominant UI library"),
            ("vercel/next.js", 93, "Next.js — full-stack React framework"),
            ("expressjs/express", 87, "Express — Node.js web framework"),
        ],
        "typescript": [
            ("microsoft/TypeScript", 94, "TypeScript compiler itself"),
            ("vercel/next.js", 92, "Next.js — TypeScript-first"),
            ("trpc/trpc", 88, "tRPC — end-to-end typesafe APIs"),
        ],
        "go": [
            ("kubernetes/kubernetes", 97, "Kubernetes — container orchestration"),
            ("docker/cli", 90, "Docker CLI — container management"),
            ("gin-gonic/gin", 86, "Gin — Go web framework"),
        ],
        "rust": [
            ("denoland/deno", 93, "Deno — modern JavaScript runtime in Rust"),
            ("tauri-apps/tauri", 91, "Tauri — desktop apps with Rust"),
            ("tokio-rs/tokio", 88, "Tokio — async runtime for Rust"),
        ],
        "react": [
            ("facebook/react", 97, "React core library"),
            ("vercel/next.js", 94, "Next.js — React framework"),
            ("pmndrs/zustand", 89, "Zustand — lightweight React state management"),
        ],
        "machine-learning": [
            ("pytorch/pytorch", 96, "PyTorch — deep learning framework"),
            ("huggingface/transformers", 94, "Transformers — NLP models"),
            ("scikit-learn/scikit-learn", 90, "Scikit-learn — classical ML"),
        ],
    }

    results = []
    seen = set()
    for skill in skills:
        repos = SKILL_REPOS.get(skill.lower(), [])
        for repo_name, score, reason in repos:
            if repo_name not in seen:
                seen.add(repo_name)
                results.append({
                    "repository": repo_name,
                    "score": score,
                    "reason": reason,
                    "language": None,
                    "stars": 0,
                    "topics": [],
                })

    return results[:limit]
