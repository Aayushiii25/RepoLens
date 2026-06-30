from pydantic import BaseModel
from typing import Optional


class LanguageDTO(BaseModel):
    name: str
    color: Optional[str] = None
    percentage: float = 0


class ContributorDTO(BaseModel):
    login: str
    avatar_url: Optional[str] = None
    name: Optional[str] = None


class ReleaseDTO(BaseModel):
    tag: str
    name: str
    published_at: Optional[str] = None
    description: Optional[str] = None
    is_latest: bool = False


class LabelDTO(BaseModel):
    name: str
    color: Optional[str] = None


class IssueDTO(BaseModel):
    number: int
    title: str
    body: Optional[str] = None
    created_at: Optional[str] = None
    author: Optional[str] = None
    author_avatar: Optional[str] = None
    labels: list[LabelDTO] = []
    comment_count: int = 0
    difficulty: str = "Medium"


class CommitDTO(BaseModel):
    message: str
    date: Optional[str] = None
    author: str
    avatar: Optional[str] = None


class HealthDTO(BaseModel):
    overall: int
    activity: int
    community: int
    documentation: int
    security: int
    maintainability: int


class RepositoryDetailDTO(BaseModel):
    github_id: str
    full_name: str
    owner: str
    owner_avatar: Optional[str] = None
    name: str
    description: Optional[str] = None
    url: Optional[str] = None
    homepage: Optional[str] = None
    stars: int = 0
    forks: int = 0
    watchers: int = 0
    language: Optional[str] = None
    language_color: Optional[str] = None
    languages: list[LanguageDTO] = []
    topics: list[str] = []
    open_issues: int = 0
    closed_issues: int = 0
    open_prs: int = 0
    merged_prs: int = 0
    commit_count: int = 0
    license: Optional[str] = None
    license_name: Optional[str] = None
    default_branch: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    pushed_at: Optional[str] = None
    health: HealthDTO
    contributors: list[ContributorDTO] = []
    contributor_count: int = 0
    releases: list[ReleaseDTO] = []
    readme: Optional[str] = None
    has_wiki: bool = False
    has_issues: bool = False
    has_code_of_conduct: bool = False
    has_funding: bool = False
    has_security_policy: bool = False
