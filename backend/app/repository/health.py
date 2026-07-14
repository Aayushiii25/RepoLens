"""
Repository Health Engine

Provides detailed repository health scoring with breakdowns, trend indicators,
and descriptive labels. Extracted from the inline health calculation in
github/client.py to be a standalone, reusable service.

Scoring dimensions:
  - Activity:        Push recency, PR velocity, commit frequency
  - Community:       Contributor count, stars, forks, code of conduct
  - Documentation:   README quality, wiki, docs depth
  - Security:        License, security policy, dependency updates
  - Maintainability: Issue close rate, release cadence
  - Overall:         Weighted combination of all dimensions
"""

import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def _label_for_score(score: int) -> str:
    """Return a human-readable label for a health score."""
    if score >= 90:
        return "Excellent"
    elif score >= 75:
        return "Good"
    elif score >= 60:
        return "Fair"
    elif score >= 40:
        return "Needs Improvement"
    else:
        return "Critical"


def _trend_indicator(score: int) -> str:
    """Return a trend arrow based on score level."""
    if score >= 85:
        return "trending_up"
    elif score >= 60:
        return "stable"
    else:
        return "trending_down"


def calculate_detailed_health(repo_data: dict) -> dict:
    """
    Calculate a detailed health breakdown for a repository.

    Args:
        repo_data: Raw repository data dict (from GitHub client transform)

    Returns:
        Dict with overall score, dimension scores, labels, and recommendations
    """
    # Extract metrics
    stars = repo_data.get("stars", 0)
    forks = repo_data.get("forks", 0)
    open_issues = repo_data.get("open_issues", 0)
    closed_issues = repo_data.get("closed_issues", 0)
    open_prs = repo_data.get("open_prs", 0)
    merged_prs = repo_data.get("merged_prs", 0)
    commit_count = repo_data.get("commit_count", 0)
    contributor_count = repo_data.get("contributor_count", 0)
    releases = repo_data.get("releases", [])
    readme = repo_data.get("readme")
    has_wiki = repo_data.get("has_wiki", False)
    has_code_of_conduct = repo_data.get("has_code_of_conduct", False)
    has_security_policy = repo_data.get("has_security_policy", False)
    has_funding = repo_data.get("has_funding", False)
    license_name = repo_data.get("license")
    pushed_at = repo_data.get("pushed_at")

    # ── Activity Score ──────────────────────────────────────────
    days_since_push = 365
    if pushed_at:
        try:
            pushed = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
            days_since_push = (datetime.now(timezone.utc) - pushed).days
        except Exception:
            pass

    if days_since_push <= 1:
        recency = 100
    elif days_since_push <= 7:
        recency = 90
    elif days_since_push <= 30:
        recency = 75
    elif days_since_push <= 90:
        recency = 55
    elif days_since_push <= 365:
        recency = 30
    else:
        recency = 10

    pr_activity = min(100, (merged_prs + open_prs) * 2)
    commit_score = min(100, commit_count // 10) if commit_count else 20
    activity_score = int(recency * 0.5 + pr_activity * 0.3 + commit_score * 0.2)

    activity_detail = {
        "score": min(activity_score, 100),
        "label": _label_for_score(activity_score),
        "trend": _trend_indicator(activity_score),
        "factors": {
            "push_recency": f"{days_since_push} days ago",
            "merged_prs": merged_prs,
            "open_prs": open_prs,
            "total_commits": commit_count,
        },
    }

    # ── Community Score ─────────────────────────────────────────
    community_factors = []
    community_factors.append(min(100, contributor_count * 5))
    community_factors.append(min(100, stars // 100))
    community_factors.append(min(100, forks * 3))
    community_factors.append(100 if has_code_of_conduct else 0)
    community_factors.append(100 if has_funding else 0)
    community_score = int(sum(community_factors) / len(community_factors))

    community_detail = {
        "score": min(community_score, 100),
        "label": _label_for_score(community_score),
        "trend": _trend_indicator(community_score),
        "factors": {
            "contributors": contributor_count,
            "stars": stars,
            "forks": forks,
            "has_code_of_conduct": has_code_of_conduct,
            "has_funding": has_funding,
        },
    }

    # ── Documentation Score ─────────────────────────────────────
    has_readme = bool(readme)
    readme_length = len(readme) if readme else 0
    doc_factors = []
    doc_factors.append(100 if has_readme else 0)
    doc_factors.append(100 if has_wiki else 0)
    doc_factors.append(min(100, readme_length // 50) if has_readme else 0)
    documentation_score = int(sum(doc_factors) / len(doc_factors))

    documentation_detail = {
        "score": min(documentation_score, 100),
        "label": _label_for_score(documentation_score),
        "trend": _trend_indicator(documentation_score),
        "factors": {
            "has_readme": has_readme,
            "readme_length": readme_length,
            "has_wiki": has_wiki,
        },
    }

    # ── Security Score ──────────────────────────────────────────
    sec_factors = []
    sec_factors.append(100 if license_name else 0)
    sec_factors.append(100 if has_security_policy else 0)
    security_score = int(sum(sec_factors) / len(sec_factors))

    security_detail = {
        "score": min(security_score, 100),
        "label": _label_for_score(security_score),
        "trend": _trend_indicator(security_score),
        "factors": {
            "has_license": bool(license_name),
            "license": license_name,
            "has_security_policy": has_security_policy,
        },
    }

    # ── Maintainability Score ───────────────────────────────────
    total_issues = open_issues + closed_issues
    issue_close_rate = (closed_issues / total_issues * 100) if total_issues > 0 else 50
    release_count = len(releases)
    release_score = min(100, release_count * 20)
    maintainability_score = int(issue_close_rate * 0.6 + release_score * 0.4)

    maintainability_detail = {
        "score": min(maintainability_score, 100),
        "label": _label_for_score(maintainability_score),
        "trend": _trend_indicator(maintainability_score),
        "factors": {
            "issue_close_rate": f"{issue_close_rate:.1f}%",
            "open_issues": open_issues,
            "closed_issues": closed_issues,
            "releases": release_count,
        },
    }

    # ── Overall Score ───────────────────────────────────────────
    overall = int(
        activity_score * 0.25
        + community_score * 0.20
        + documentation_score * 0.20
        + security_score * 0.15
        + maintainability_score * 0.20
    )
    overall = min(overall, 100)

    # ── Recommendations ─────────────────────────────────────────
    recommendations = []
    if not has_readme:
        recommendations.append("Add a comprehensive README to improve documentation score")
    if not license_name:
        recommendations.append("Add a license to improve security and legal clarity")
    if not has_security_policy:
        recommendations.append("Add a SECURITY.md file with vulnerability reporting instructions")
    if not has_code_of_conduct:
        recommendations.append("Add a Code of Conduct to build community trust")
    if days_since_push > 90:
        recommendations.append("Repository hasn't been updated recently — may indicate inactivity")
    if release_count == 0:
        recommendations.append("Publish releases to improve maintainability perception")
    if total_issues > 0 and issue_close_rate < 50:
        recommendations.append("Improve issue close rate — many open issues signal backlog")

    return {
        "overall": {
            "score": overall,
            "label": _label_for_score(overall),
            "trend": _trend_indicator(overall),
        },
        "dimensions": {
            "activity": activity_detail,
            "community": community_detail,
            "documentation": documentation_detail,
            "security": security_detail,
            "maintainability": maintainability_detail,
        },
        "recommendations": recommendations[:5],  # Top 5 recommendations
        "metadata": {
            "scored_at": datetime.now(timezone.utc).isoformat(),
            "version": "1.0",
        },
    }
