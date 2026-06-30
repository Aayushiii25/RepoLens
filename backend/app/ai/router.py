from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from app.ml.llm import llm_gateway

router = APIRouter(prefix="/api/v1/ai", tags=["AI Features"])

class ContributionCoachRequest(BaseModel):
    issue_id: int
    user_skills: List[str]
    repo_name: str

class ContributionCoachResponse(BaseModel):
    steps: List[str]
    estimated_time: str
    confidence: int

@router.post("/contribution-coach", response_model=ContributionCoachResponse)
async def contribution_coach(req: ContributionCoachRequest):
    """Step-by-step contribution guidance using LLM."""
    if not llm_gateway.model:
        return ContributionCoachResponse(
            steps=[
                "Read repository architecture",
                "Study auth package",
                f"Open issue #{req.issue_id}",
                "Modify middleware",
                "Run tests"
            ],
            estimated_time="6 hours",
            confidence=91
        )
    
    # Placeholder for real LLM dynamic coach generation
    return ContributionCoachResponse(
        steps=["Setup local dev", "Reproduce issue", "Write failing test", "Fix code", "Submit PR"],
        estimated_time="2 days",
        confidence=85
    )

class ChatRequest(BaseModel):
    message: str
    history: List[dict] = []

@router.post("/repositories/{owner}/{name}/chat")
async def repository_chat(owner: str, name: str, req: ChatRequest):
    """RAG-powered chat against repository codebase and docs."""
    # Placeholder for Qdrant + LLM RAG
    return {"reply": f"This is a placeholder reply about {owner}/{name}. RAG implementation pending.", "sources": []}

@router.post("/repositories/compare")
async def compare_repositories(repo_names: List[str]):
    """Compare multiple repositories side-by-side using AI."""
    # Placeholder for cross-repo AI comparison
    return {"comparison": f"Comparison between {', '.join(repo_names)}"}
