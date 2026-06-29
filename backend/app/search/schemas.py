from pydantic import BaseModel
from typing import Optional


class RepositoryDTO(BaseModel):
    id: int
    full_name: str
    owner: str
    name: str
    description: Optional[str] = None
    language: Optional[str] = None
    stars: int = 0
    forks: int = 0
    open_issues: int = 0
    topics: list[str] = []
    license: Optional[str] = None
    default_branch: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    query: str
    count: int
    results: list[RepositoryDTO]
    cached: bool = False
