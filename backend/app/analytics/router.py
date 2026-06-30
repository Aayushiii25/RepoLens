from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])

@router.get("/trending")
async def trending_repositories():
    """Get trending repositories."""
    # Placeholder for actual trending logic
    return [
        {"name": "vercel/next.js", "stars_today": 150},
        {"name": "fastapi/fastapi", "stars_today": 120}
    ]

@router.get("/languages")
async def language_trends():
    """Get programming language trends over time."""
    return {"TypeScript": "+5%", "Python": "+12%", "Rust": "+20%"}

@router.get("/topics")
async def technology_trends():
    """Get technology and topic trends."""
    return {"machine-learning": "+40%", "web3": "-15%"}
