import logging
import json
import google.generativeai as genai
from app.core.config import get_settings
from app.core.cache import cache

logger = logging.getLogger(__name__)


class LLMGateway:
    """
    Centralized gateway for all LLM calls.

    All AI features route through this single gateway, providing:
      - Centralized prompt management
      - Response caching (avoid redundant LLM calls)
      - Rate limiting awareness
      - Model swappability (change one line to switch providers)
    """

    def __init__(self):
        settings = get_settings()
        self.api_key = getattr(settings, "GEMINI_API_KEY", None)
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("LLM Gateway initialized with Gemini.")
        else:
            self.model = None
            logger.warning("GEMINI_API_KEY not set. AI features will return mock data.")

    async def _generate(self, prompt: str, cache_key: str = None, cache_ttl: int = 86400) -> str:
        """
        Internal method to call the LLM with optional caching.
        Returns the raw text response.
        """
        if cache_key:
            cached = cache.get(cache_key)
            if cached:
                logger.info(f"LLM cache HIT: {cache_key}")
                return cached

        if not self.model:
            return None

        try:
            response = await self.model.generate_content_async(prompt)
            text = response.text

            if cache_key:
                cache.set(cache_key, text, ttl=cache_ttl)

            return text
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return None

    def _parse_json(self, text: str) -> dict:
        """Extract JSON from LLM response, handling markdown code fences."""
        if not text:
            return {}
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            logger.warning("Failed to parse LLM JSON response")
            return {}

    async def generate_repository_summary(self, repo_data: dict) -> dict:
        """Generate an AI-powered summary of a repository."""
        repo_name = repo_data.get("full_name", "unknown")
        cache_key = f"llm:summary:{repo_name}"

        if not self.model:
            return {
                "summary": f"{repo_name} is an open-source project that demonstrates modern software engineering practices. "
                          f"It's written primarily in {repo_data.get('language', 'multiple languages')} and has "
                          f"{repo_data.get('stars', 0):,} stars on GitHub.",
                "architecture": f"The project follows a modular architecture with clear separation of concerns. "
                               f"Key areas include the core library, API layer, and documentation.",
                "difficulty": "Intermediate",
                "learning_outcomes": [
                    f"Understanding {repo_data.get('language', 'modern')} best practices and patterns",
                    "Learning how to contribute to large-scale open-source projects",
                    "Gaining experience with the project's testing and CI/CD pipeline",
                ],
            }

        prompt = f"""Analyze this repository and provide a summary, architecture overview, difficulty level (Beginner/Intermediate/Advanced), and 3 learning outcomes for contributors.
Return ONLY valid JSON.

Repository: {repo_data.get('full_name')}
Description: {repo_data.get('description')}
Language: {repo_data.get('language')}
Topics: {', '.join(repo_data.get('topics', []))}
Stars: {repo_data.get('stars', 0)}
Readme snippet: {str(repo_data.get('readme'))[:1500]}

Expected JSON format:
{{
    "summary": "string",
    "architecture": "string",
    "difficulty": "string",
    "learning_outcomes": ["string", "string", "string"]
}}"""

        text = await self._generate(prompt, cache_key=cache_key)
        result = self._parse_json(text) if text else {}

        return result or {
            "summary": "Failed to generate AI summary.",
            "architecture": "N/A",
            "difficulty": "Unknown",
            "learning_outcomes": [],
        }

    async def generate_contribution_guide(self, repo_name: str, issue_id: int, user_skills: list[str]) -> dict:
        """Generate step-by-step contribution guidance for an issue."""
        cache_key = f"llm:coach:{repo_name}:{issue_id}:{'_'.join(sorted(user_skills))}"

        if not self.model:
            return {
                "steps": [
                    f"Fork and clone {repo_name} to your local machine",
                    "Read the CONTRIBUTING.md and project documentation",
                    f"Locate the relevant code for issue #{issue_id}",
                    "Write a failing test that captures the expected behavior",
                    "Implement the fix/feature with clear, documented code",
                    "Run the test suite to ensure no regressions",
                    "Submit a Pull Request with a descriptive title and body",
                ],
                "estimated_time": "4-8 hours",
                "confidence": 85,
                "prerequisites": [
                    f"Familiarity with {', '.join(user_skills[:3])}",
                    "Git and GitHub workflow knowledge",
                    "Local development environment setup",
                ],
            }

        prompt = f"""You are a senior open-source mentor. Generate a step-by-step contribution guide.
Return ONLY valid JSON.

Repository: {repo_name}
Issue: #{issue_id}
Developer skills: {', '.join(user_skills)}

Expected JSON format:
{{
    "steps": ["step 1", "step 2", ...],
    "estimated_time": "X hours/days",
    "confidence": 85,
    "prerequisites": ["prerequisite 1", "prerequisite 2"]
}}"""

        text = await self._generate(prompt, cache_key=cache_key)
        result = self._parse_json(text) if text else {}

        return result or {
            "steps": ["Setup local dev", "Reproduce issue", "Write failing test", "Fix code", "Submit PR"],
            "estimated_time": "2 days",
            "confidence": 75,
            "prerequisites": [],
        }

    async def compare_repositories(self, repo_names: list[str], repo_data_list: list[dict]) -> dict:
        """Compare multiple repositories using AI analysis."""
        cache_key = f"llm:compare:{'_'.join(sorted(repo_names))}"

        summaries = []
        for rd in repo_data_list:
            summaries.append(
                f"- {rd.get('full_name', 'unknown')}: {rd.get('description', 'N/A')} "
                f"| Language: {rd.get('language', 'N/A')} | Stars: {rd.get('stars', 0)} "
                f"| Forks: {rd.get('forks', 0)}"
            )

        if not self.model:
            # Generate structured mock comparison
            repos = []
            for rd in repo_data_list:
                repos.append({
                    "name": rd.get("full_name", "unknown"),
                    "strengths": [
                        f"Written in {rd.get('language', 'modern languages')}",
                        f"{rd.get('stars', 0):,} GitHub stars",
                    ],
                    "weaknesses": ["Requires further analysis"],
                })
            return {
                "comparison": repos,
                "recommendation": f"All {len(repo_names)} repositories are solid choices. "
                                  "Choose based on your tech stack preference and project requirements.",
                "winner": repo_names[0] if repo_names else "N/A",
            }

        prompt = f"""Compare these repositories for a developer choosing between them.
Return ONLY valid JSON.

Repositories:
{chr(10).join(summaries)}

Expected JSON format:
{{
    "comparison": [
        {{
            "name": "owner/repo",
            "strengths": ["strength 1", "strength 2"],
            "weaknesses": ["weakness 1"]
        }}
    ],
    "recommendation": "Overall recommendation string",
    "winner": "owner/repo"
}}"""

        text = await self._generate(prompt, cache_key=cache_key)
        result = self._parse_json(text) if text else {}
        return result or {"comparison": [], "recommendation": "Unable to compare", "winner": "N/A"}

    async def explain_repository(self, repo_data: dict) -> dict:
        """Generate a beginner-friendly explanation of what a repository does."""
        repo_name = repo_data.get("full_name", "unknown")
        cache_key = f"llm:explain:{repo_name}"

        if not self.model:
            desc = repo_data.get("description", "")
            lang = repo_data.get("language", "various languages")
            return {
                "what_it_does": desc or f"{repo_name} is an open-source project.",
                "who_its_for": f"Developers working with {lang} who want to contribute to open source.",
                "how_it_works": f"The project is built primarily in {lang} and follows modern development practices.",
                "getting_started": f"Visit github.com/{repo_name} and read the README and CONTRIBUTING.md files.",
            }

        prompt = f"""Explain this repository in simple terms for a developer who has never seen it before.
Return ONLY valid JSON.

Repository: {repo_data.get('full_name')}
Description: {repo_data.get('description')}
Language: {repo_data.get('language')}
Topics: {', '.join(repo_data.get('topics', []))}
Stars: {repo_data.get('stars', 0)}
Readme snippet: {str(repo_data.get('readme'))[:1000]}

Expected JSON format:
{{
    "what_it_does": "string",
    "who_its_for": "string",
    "how_it_works": "string",
    "getting_started": "string"
}}"""

        text = await self._generate(prompt, cache_key=cache_key)
        return self._parse_json(text) if text else {
            "what_it_does": "Unable to generate explanation.",
            "who_its_for": "N/A",
            "how_it_works": "N/A",
            "getting_started": "N/A",
        }


llm_gateway = LLMGateway()
