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

    async def search_repositories(self, query: str, first: int = 20) -> list[dict]:
        """Search GitHub repositories via GraphQL. Returns parsed list of repo dicts."""
        if not self.token:
            logger.warning("GITHUB_TOKEN is not set — returning empty results.")
            return []

        variables = {"query": query, "first": first}
        payload = {"query": SEARCH_REPOS_QUERY, "variables": variables}

        try:
            response = await self.client.post(GITHUB_GRAPHQL_URL, json=payload)
            response.raise_for_status()
            data = response.json()

            if "errors" in data:
                logger.error(f"GitHub GraphQL errors: {data['errors']}")
                return []

            nodes = data.get("data", {}).get("search", {}).get("nodes", [])
            return [self._transform(node) for node in nodes if node]

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                logger.error("GitHub token is invalid or expired.")
            elif e.response.status_code == 403:
                logger.error("GitHub API rate limit exceeded.")
            else:
                logger.error(f"GitHub API error: {e.response.status_code}")
            return []
        except httpx.RequestError as e:
            logger.error(f"Network error calling GitHub: {e}")
            return []

    def _transform(self, node: dict) -> dict:
        """Transform raw GraphQL node into a clean dict matching our schema."""
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

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()


# Application-wide singleton
github_client = GitHubClient()
