from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.ml.llm import llm_gateway
from app.github.client import github_client
from app.core.cache import cache

router = APIRouter(prefix="/api/v1/ai", tags=["AI Features"])


# ── Contribution Coach ──────────────────────────────────────────

class ContributionCoachRequest(BaseModel):
    issue_id: int
    user_skills: List[str]
    repo_name: str


class ContributionCoachResponse(BaseModel):
    steps: List[str]
    estimated_time: str
    confidence: int
    prerequisites: List[str] = []


@router.post("/contribution-coach", response_model=ContributionCoachResponse)
async def contribution_coach(req: ContributionCoachRequest):
    """
    Generate step-by-step contribution guidance for a specific issue.

    Uses LLM to analyze the repository context and issue, then produces
    a personalized guide tailored to the developer's skill set.
    """
    result = await llm_gateway.generate_contribution_guide(
        repo_name=req.repo_name,
        issue_id=req.issue_id,
        user_skills=req.user_skills,
    )
    return ContributionCoachResponse(**result)


# ── Repository Explanation ──────────────────────────────────────

class ExplainRequest(BaseModel):
    owner: str
    name: str


@router.post("/explain")
async def explain_repository(req: ExplainRequest):
    """
    Generate a beginner-friendly explanation of what a repository does.

    Returns structured sections: what it does, who it's for, how it works,
    and how to get started contributing.
    """
    repo_data = await github_client.get_repository(req.owner, req.name)
    if not repo_data:
        raise HTTPException(status_code=404, detail="Repository not found")

    return await llm_gateway.explain_repository(repo_data)


# ── Repository Comparison ──────────────────────────────────────

class CompareRequest(BaseModel):
    repo_names: List[str]


@router.post("/repositories/compare")
async def compare_repositories(req: CompareRequest):
    """
    Compare multiple repositories side-by-side using AI analysis.

    Fetches data for each repository, then uses LLM to generate
    structured comparison with strengths, weaknesses, and recommendations.
    """
    if len(req.repo_names) < 2:
        raise HTTPException(status_code=400, detail="Provide at least 2 repositories to compare")
    if len(req.repo_names) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 repositories for comparison")

    repo_data_list = []
    for repo_name in req.repo_names:
        parts = repo_name.split("/")
        if len(parts) != 2:
            continue
        data = await github_client.get_repository(parts[0], parts[1])
        if data:
            repo_data_list.append(data)

    if len(repo_data_list) < 2:
        raise HTTPException(status_code=404, detail="Could not fetch data for enough repositories")

    return await llm_gateway.compare_repositories(req.repo_names, repo_data_list)


# ── Repository Chat ─────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    history: List[dict] = []


@router.post("/repositories/{owner}/{name}/chat")
async def repository_chat(owner: str, name: str, req: ChatRequest):
    """
    RAG-powered chat against repository codebase and documentation.

    Uses repository context (README, description, topics) combined with
    LLM to answer questions about the repository.
    """
    # Get repository context
    repo_data = await github_client.get_repository(owner, name)
    if not repo_data:
        raise HTTPException(status_code=404, detail="Repository not found")

    readme = repo_data.get("readme", "")
    description = repo_data.get("description", "")
    language = repo_data.get("language", "")
    topics = repo_data.get("topics", [])

    # Build context-aware prompt
    context = f"""Repository: {owner}/{name}
Description: {description}
Language: {language}
Topics: {', '.join(topics)}
README (first 2000 chars): {str(readme)[:2000]}"""

    if not llm_gateway.model:
        # Smart mock response based on question keywords
        msg = req.message.lower()
        if "how" in msg and ("start" in msg or "contribute" in msg or "setup" in msg):
            reply = f"To get started with {owner}/{name}, clone the repository and follow the README instructions. The project uses {language} and you'll need the appropriate development environment set up."
        elif "what" in msg:
            reply = f"{owner}/{name} is {description or 'an open-source project'}. It's primarily built with {language} and covers topics like {', '.join(topics[:5])}."
        elif "architecture" in msg or "structure" in msg:
            reply = f"The {owner}/{name} repository follows a modular architecture. Check the project's directory structure and README for detailed architecture documentation."
        else:
            reply = f"Based on the {owner}/{name} repository (built with {language}): {description}. Please refer to the README for more specific information about your question."

        return {
            "reply": reply,
            "sources": [f"README.md of {owner}/{name}"],
            "context_used": True,
        }

    prompt = f"""You are a helpful assistant that answers questions about the following repository. Use the provided context to give accurate answers.

Context:
{context}

Conversation history:
{json.dumps(req.history[-5:])}

User question: {req.message}

Provide a helpful, concise answer based on the repository context above."""

    import json
    try:
        response = await llm_gateway.model.generate_content_async(prompt)
        return {
            "reply": response.text,
            "sources": [f"README.md of {owner}/{name}"],
            "context_used": True,
        }
    except Exception as e:
        return {
            "reply": f"I couldn't process that question right now. Error: {str(e)}",
            "sources": [],
            "context_used": False,
        }
