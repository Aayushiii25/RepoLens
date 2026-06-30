import logging
import json
import google.generativeai as genai
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class LLMGateway:
    """Centralized gateway for all LLM calls (AI summaries, Contribution Coach)."""

    def __init__(self):
        settings = get_settings()
        # We assume GEMINI_API_KEY might be in settings
        self.api_key = getattr(settings, "GEMINI_API_KEY", None)
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("LLM Gateway initialized with Gemini.")
        else:
            self.model = None
            logger.warning("GEMINI_API_KEY not set. AI features will return mock data.")

    async def generate_repository_summary(self, repo_data: dict) -> dict:
        if not self.model:
            return {
                "summary": "This is a mock AI summary because GEMINI_API_KEY is not set in the backend.",
                "architecture": "Mock architecture description. Set GEMINI_API_KEY to enable real AI analysis.",
                "difficulty": "Intermediate",
                "learning_outcomes": [
                    "Learn about cache-first backends",
                    "Understand how to integrate GraphQL APIs",
                    "Build dynamic Next.js dashboards"
                ]
            }

        prompt = f"""
        Analyze this repository and provide a summary, architecture overview, difficulty level (Beginner/Intermediate/Advanced), and 3 learning outcomes for contributors.
        Return ONLY valid JSON.

        Repository: {repo_data.get('full_name')}
        Description: {repo_data.get('description')}
        Language: {repo_data.get('language')}
        Topics: {', '.join(repo_data.get('topics', []))}
        Readme snippet: {str(repo_data.get('readme'))[:1500]}

        Expected JSON format:
        {{
            "summary": "string",
            "architecture": "string",
            "difficulty": "string",
            "learning_outcomes": ["string", "string", "string"]
        }}
        """

        try:
            # We use run_in_executor in a real async environment, but generate_content has an async version? 
            # Actually generate_content_async is available in the gemini SDK
            response = await self.model.generate_content_async(prompt)
            
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            return json.loads(text.strip())
        except Exception as e:
            logger.error(f"LLM Generation failed: {e}")
            return {
                "summary": "Failed to generate AI summary.",
                "architecture": "N/A",
                "difficulty": "Unknown",
                "learning_outcomes": []
            }


llm_gateway = LLMGateway()
