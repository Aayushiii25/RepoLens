from sqlalchemy import Column, String, Integer, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.db.session import Base


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    github_id = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, index=True, nullable=False)
    owner = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    language = Column(String, nullable=True)
    stars = Column(Integer, default=0)
    forks = Column(Integer, default=0)
    open_issues = Column(Integer, default=0)
    topics = Column(JSON, default=list)
    license = Column(String, nullable=True)
    default_branch = Column(String, nullable=True)
    updated_at = Column(String, nullable=True)  # GitHub's pushedAt
    created_at_db = Column(DateTime, server_default=func.now())
    updated_at_db = Column(DateTime, server_default=func.now(), onupdate=func.now())
