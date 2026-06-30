import httpx
import logging
from app.core.config import get_settings

logger = logging.getLogger(__name__)

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

SEARCH_REPOS_QUERY = """
query SearchRepositories($query: String!, $first: Int!) {
  search(query: $query, type: REPOSITORY, first: $first) {
    repositoryCount
    nodes {
      ... on Repository {
        databaseId
        nameWithOwner
        owner {
          login
        }
        name
        description
        stargazerCount
        forkCount
        primaryLanguage {
          name
        }
        repositoryTopics(first: 10) {
          nodes {
            topic {
              name
            }
          }
        }
        pushedAt
        issues(states: OPEN) {
          totalCount
        }
        licenseInfo {
          spdxId
        }
        defaultBranchRef {
          name
        }
      }
    }
  }
}
"""

REPO_DETAIL_QUERY = """
query RepositoryDetail($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    databaseId
    nameWithOwner
    owner {
      login
      avatarUrl
    }
    name
    description
    url
    homepageUrl
    stargazerCount
    forkCount
    watchers {
      totalCount
    }
    primaryLanguage {
      name
      color
    }
    languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
      edges {
        node {
          name
          color
        }
        size
      }
      totalSize
    }
    repositoryTopics(first: 20) {
      nodes {
        topic {
          name
        }
      }
    }
    pushedAt
    createdAt
    updatedAt
    issues(states: OPEN) {
      totalCount
    }
    closedIssues: issues(states: CLOSED) {
      totalCount
    }
    pullRequests(states: OPEN) {
      totalCount
    }
    mergedPullRequests: pullRequests(states: MERGED) {
      totalCount
    }
    licenseInfo {
      spdxId
      name
    }
    defaultBranchRef {
      name
      target {
        ... on Commit {
          history(first: 1) {
            totalCount
          }
        }
      }
    }
    releases(first: 5, orderBy: {field: CREATED_AT, direction: DESC}) {
      nodes {
        tagName
        name
        publishedAt
        description
        isLatest
      }
    }
    mentionableUsers(first: 10) {
      nodes {
        login
        avatarUrl
        name
      }
      totalCount
    }
    object(expression: "HEAD:README.md") {
      ... on Blob {
        text
      }
    }
    hasWikiEnabled
    hasIssuesEnabled
    codeOfConduct {
      name
    }
    fundingLinks {
      url
    }
    securityPolicyUrl
  }
}
"""

REPO_ISSUES_QUERY = """
query RepositoryIssues($owner: String!, $name: String!, $first: Int!) {
  repository(owner: $owner, name: $name) {
    issues(first: $first, states: OPEN, orderBy: {field: CREATED_AT, direction: DESC}) {
      nodes {
        number
        title
        body
        createdAt
        author {
          login
          avatarUrl
        }
        labels(first: 5) {
          nodes {
            name
            color
          }
        }
        comments {
          totalCount
        }
      }
    }
  }
}
"""

REPO_ACTIVITY_QUERY = """
query RepositoryActivity($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    defaultBranchRef {
      target {
        ... on Commit {
          history(first: 10) {
            nodes {
              message
              committedDate
              author {
                name
                user {
                  login
                  avatarUrl
                }
              }
            }
          }
        }
      }
    }
  }
}
"""


class GitHubClient:
    """Singleton-style GitHub GraphQL client."""

    def __init__(self):
        settings = get_settings()
        self.token = settings.GITHUB_TOKEN
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }
            self._client = httpx.AsyncClient(
                headers=headers,
                timeout=15.0,
            )
        return self._client

    async def _query(self, query: str, variables: dict) -> dict | None:
        if not self.token:
            logger.warning("GITHUB_TOKEN is not set.")
            return None
        try:
            response = await self.client.post(
                GITHUB_GRAPHQL_URL,
                json={"query": query, "variables": variables},
            )
            response.raise_for_status()
            data = response.json()
            if "errors" in data:
                logger.error(f"GitHub GraphQL errors: {data['errors']}")
                return None
            return data.get("data")
        except httpx.HTTPStatusError as e:
            logger.error(f"GitHub API error: {e.response.status_code}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Network error: {e}")
            return None

    async def search_repositories(self, query: str, first: int = 20) -> list[dict]:
        data = await self._query(SEARCH_REPOS_QUERY, {"query": query, "first": first})
        if not data:
            return []
        nodes = data.get("search", {}).get("nodes", [])
        return [self._transform_search(node) for node in nodes if node]

    async def get_repository(self, owner: str, name: str) -> dict | None:
        data = await self._query(REPO_DETAIL_QUERY, {"owner": owner, "name": name})
        if not data or not data.get("repository"):
            return None
        return self._transform_detail(data["repository"])

    async def get_repository_issues(self, owner: str, name: str, first: int = 15) -> list[dict]:
        data = await self._query(REPO_ISSUES_QUERY, {"owner": owner, "name": name, "first": first})
        if not data or not data.get("repository"):
            return []
        nodes = data["repository"].get("issues", {}).get("nodes", [])
        return [self._transform_issue(n) for n in nodes if n]

    async def get_repository_activity(self, owner: str, name: str) -> list[dict]:
        data = await self._query(REPO_ACTIVITY_QUERY, {"owner": owner, "name": name})
        if not data or not data.get("repository"):
            return []
        ref = data["repository"].get("defaultBranchRef")
        if not ref:
            return []
        commits = ref.get("target", {}).get("history", {}).get("nodes", [])
        return [self._transform_commit(c) for c in commits if c]

    def _transform_search(self, node: dict) -> dict:
        topics = [
            t["topic"]["name"]
            for t in (node.get("repositoryTopics", {}).get("nodes", []))
        ]
        return {
            "github_id": str(node.get("databaseId", "")),
            "full_name": node.get("nameWithOwner", ""),
            "owner": node.get("owner", {}).get("login", ""),
            "name": node.get("name", ""),
            "description": node.get("description"),
            "language": (node.get("primaryLanguage") or {}).get("name"),
            "stars": node.get("stargazerCount", 0),
            "forks": node.get("forkCount", 0),
            "open_issues": node.get("issues", {}).get("totalCount", 0),
            "topics": topics,
            "license": (node.get("licenseInfo") or {}).get("spdxId"),
            "default_branch": (node.get("defaultBranchRef") or {}).get("name"),
            "updated_at": node.get("pushedAt"),
        }

    def _transform_detail(self, repo: dict) -> dict:
        topics = [t["topic"]["name"] for t in repo.get("repositoryTopics", {}).get("nodes", [])]

        # Languages with percentages
        lang_edges = repo.get("languages", {}).get("edges", [])
        total_size = repo.get("languages", {}).get("totalSize", 1)
        languages = [
            {
                "name": e["node"]["name"],
                "color": e["node"].get("color"),
                "percentage": round((e["size"] / total_size) * 100, 1) if total_size else 0,
            }
            for e in lang_edges
        ]

        # Contributors
        contributors = [
            {
                "login": u["login"],
                "avatar_url": u["avatarUrl"],
                "name": u.get("name"),
            }
            for u in repo.get("mentionableUsers", {}).get("nodes", [])
        ]

        # Releases
        releases = [
            {
                "tag": r["tagName"],
                "name": r.get("name") or r["tagName"],
                "published_at": r.get("publishedAt"),
                "description": r.get("description"),
                "is_latest": r.get("isLatest", False),
            }
            for r in repo.get("releases", {}).get("nodes", [])
        ]

        # Health calculation
        health = self._calculate_health(repo)

        # Readme
        readme_obj = repo.get("object")
        readme = readme_obj.get("text") if readme_obj else None

        open_issues = repo.get("issues", {}).get("totalCount", 0)
        closed_issues = repo.get("closedIssues", {}).get("totalCount", 0)
        open_prs = repo.get("pullRequests", {}).get("totalCount", 0)
        merged_prs = repo.get("mergedPullRequests", {}).get("totalCount", 0)

        commit_count = 0
        branch_ref = repo.get("defaultBranchRef")
        if branch_ref:
            commit_count = branch_ref.get("target", {}).get("history", {}).get("totalCount", 0)

        return {
            "github_id": str(repo.get("databaseId", "")),
            "full_name": repo.get("nameWithOwner", ""),
            "owner": repo.get("owner", {}).get("login", ""),
            "owner_avatar": repo.get("owner", {}).get("avatarUrl", ""),
            "name": repo.get("name", ""),
            "description": repo.get("description"),
            "url": repo.get("url"),
            "homepage": repo.get("homepageUrl"),
            "stars": repo.get("stargazerCount", 0),
            "forks": repo.get("forkCount", 0),
            "watchers": repo.get("watchers", {}).get("totalCount", 0),
            "language": (repo.get("primaryLanguage") or {}).get("name"),
            "language_color": (repo.get("primaryLanguage") or {}).get("color"),
            "languages": languages,
            "topics": topics,
            "open_issues": open_issues,
            "closed_issues": closed_issues,
            "open_prs": open_prs,
            "merged_prs": merged_prs,
            "commit_count": commit_count,
            "license": (repo.get("licenseInfo") or {}).get("spdxId"),
            "license_name": (repo.get("licenseInfo") or {}).get("name"),
            "default_branch": (branch_ref or {}).get("name"),
            "created_at": repo.get("createdAt"),
            "updated_at": repo.get("updatedAt"),
            "pushed_at": repo.get("pushedAt"),
            "health": health,
            "contributors": contributors,
            "contributor_count": repo.get("mentionableUsers", {}).get("totalCount", 0),
            "releases": releases,
            "readme": readme,
            "has_wiki": repo.get("hasWikiEnabled", False),
            "has_issues": repo.get("hasIssuesEnabled", False),
            "has_code_of_conduct": repo.get("codeOfConduct") is not None,
            "has_funding": len(repo.get("fundingLinks", [])) > 0,
            "has_security_policy": repo.get("securityPolicyUrl") is not None,
        }

    def _calculate_health(self, repo: dict) -> dict:
        stars = repo.get("stargazerCount", 0)
        forks = repo.get("forkCount", 0)
        open_issues = repo.get("issues", {}).get("totalCount", 0)
        closed_issues = repo.get("closedIssues", {}).get("totalCount", 0)
        open_prs = repo.get("pullRequests", {}).get("totalCount", 0)
        merged_prs = repo.get("mergedPullRequests", {}).get("totalCount", 0)
        has_wiki = repo.get("hasWikiEnabled", False)
        has_coc = repo.get("codeOfConduct") is not None
        has_security = repo.get("securityPolicyUrl") is not None
        readme_obj = repo.get("object")
        has_readme = readme_obj is not None and readme_obj.get("text")
        has_license = repo.get("licenseInfo") is not None
        contributors = repo.get("mentionableUsers", {}).get("totalCount", 0)
        releases = len(repo.get("releases", {}).get("nodes", []))

        # Activity score: based on recency, commits, PRs
        from datetime import datetime, timezone
        pushed_at = repo.get("pushedAt")
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
        activity_score = int(recency * 0.6 + pr_activity * 0.4)

        # Community score
        community_factors = []
        community_factors.append(min(100, contributors * 5))
        community_factors.append(min(100, stars // 100))
        community_factors.append(min(100, forks * 3))
        community_factors.append(100 if has_coc else 0)
        community_score = int(sum(community_factors) / len(community_factors))

        # Documentation score
        doc_factors = []
        doc_factors.append(100 if has_readme else 0)
        doc_factors.append(100 if has_wiki else 0)
        doc_factors.append(min(100, len(has_readme) // 50) if has_readme else 0)
        documentation_score = int(sum(doc_factors) / len(doc_factors))

        # Security score
        sec_factors = []
        sec_factors.append(100 if has_license else 0)
        sec_factors.append(100 if has_security else 0)
        security_score = int(sum(sec_factors) / len(sec_factors))

        # Maintainability
        total_issues = open_issues + closed_issues
        issue_close_rate = (closed_issues / total_issues * 100) if total_issues > 0 else 50
        release_score = min(100, releases * 20)
        maintainability_score = int(issue_close_rate * 0.6 + release_score * 0.4)

        overall = int(
            activity_score * 0.25
            + community_score * 0.2
            + documentation_score * 0.2
            + security_score * 0.15
            + maintainability_score * 0.2
        )

        return {
            "overall": min(overall, 100),
            "activity": min(activity_score, 100),
            "community": min(community_score, 100),
            "documentation": min(documentation_score, 100),
            "security": min(security_score, 100),
            "maintainability": min(maintainability_score, 100),
        }

    def _transform_issue(self, node: dict) -> dict:
        labels = [
            {"name": l["name"], "color": l.get("color")}
            for l in node.get("labels", {}).get("nodes", [])
        ]
        is_good_first = any(l["name"].lower() in ("good first issue", "good-first-issue", "beginner") for l in labels)
        has_bug = any(l["name"].lower() in ("bug", "fix") for l in labels)
        has_feature = any(l["name"].lower() in ("enhancement", "feature", "feature request") for l in labels)
        has_docs = any(l["name"].lower() in ("documentation", "docs") for l in labels)

        if is_good_first or has_docs:
            difficulty = "Easy"
        elif has_bug:
            difficulty = "Medium"
        elif has_feature:
            difficulty = "Hard"
        else:
            difficulty = "Medium"

        return {
            "number": node.get("number"),
            "title": node.get("title"),
            "body": (node.get("body") or "")[:300],
            "created_at": node.get("createdAt"),
            "author": node.get("author", {}).get("login") if node.get("author") else None,
            "author_avatar": node.get("author", {}).get("avatarUrl") if node.get("author") else None,
            "labels": labels,
            "comment_count": node.get("comments", {}).get("totalCount", 0),
            "difficulty": difficulty,
        }

    def _transform_commit(self, node: dict) -> dict:
        author = node.get("author", {})
        user = author.get("user") or {}
        return {
            "message": (node.get("message") or "").split("\n")[0],
            "date": node.get("committedDate"),
            "author": user.get("login") or author.get("name", "Unknown"),
            "avatar": user.get("avatarUrl"),
        }

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()


# Application-wide singleton
github_client = GitHubClient()
