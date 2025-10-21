from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    Float,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional

from app.core.database import Base


class GitHubUser(Base):
    """GitHub user model for storing user information."""

    __tablename__ = "github_users"

    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(Integer, unique=True, nullable=False, index=True)
    login = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    type = Column(String(50), nullable=False, default="User")  # User, Organization
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    # Relationships
    repositories = relationship("Repository", back_populates="owner")
    issues = relationship("Issue", back_populates="author")
    pull_requests = relationship("PullRequest", back_populates="author")
    commits = relationship("Commit", back_populates="author")


class Repository(Base):
    """GitHub repository model."""

    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    full_name = Column(String(500), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    url = Column(String(500), nullable=False)
    clone_url = Column(String(500), nullable=False)
    default_branch = Column(String(255), nullable=False, default="main")
    language = Column(String(100), nullable=True)
    size = Column(Integer, nullable=False, default=0)
    stargazers_count = Column(Integer, nullable=False, default=0)
    forks_count = Column(Integer, nullable=False, default=0)
    open_issues_count = Column(Integer, nullable=False, default=0)
    is_private = Column(Boolean, nullable=False, default=False)
    is_fork = Column(Boolean, nullable=False, default=False)
    owner_id = Column(Integer, ForeignKey("github_users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )
    last_synced_at = Column(DateTime, nullable=True)

    # Relationships
    owner = relationship("GitHubUser", back_populates="repositories")
    issues = relationship("Issue", back_populates="repository")
    pull_requests = relationship("PullRequest", back_populates="repository")
    commits = relationship("Commit", back_populates="repository")


class Issue(Base):
    """GitHub issue model."""

    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(Integer, unique=True, nullable=False, index=True)
    number = Column(Integer, nullable=False, index=True)
    title = Column(String(500), nullable=False, index=True)
    body = Column(Text, nullable=True)
    state = Column(String(50), nullable=False, index=True)  # open, closed
    labels = Column(Text, nullable=True)  # JSON string of labels
    assignees = Column(Text, nullable=True)  # JSON string of assignee logins
    milestone = Column(String(255), nullable=True)
    url = Column(String(500), nullable=False)

    # Time tracking
    created_at = Column(DateTime, nullable=False, index=True)
    updated_at = Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )
    closed_at = Column(DateTime, nullable=True, index=True)

    # Effort tracking
    estimated_hours = Column(Float, nullable=True)
    actual_hours = Column(Float, nullable=True)
    story_points = Column(Integer, nullable=True)
    complexity_score = Column(Float, nullable=True)

    # Foreign keys
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("github_users.id"), nullable=False)

    # Relationships
    repository = relationship("Repository", back_populates="issues")
    author = relationship("GitHubUser", back_populates="issues")
    pull_requests = relationship("PullRequest", back_populates="linked_issue")

    @property
    def resolution_time_hours(self) -> Optional[float]:
        """Calculate resolution time in hours if issue is closed."""
        if self.closed_at and self.created_at:
            delta = self.closed_at - self.created_at
            return delta.total_seconds() / 3600
        return None

    @property
    def is_closed(self) -> bool:
        """Check if issue is closed."""
        return self.state == "closed"


class PullRequest(Base):
    """GitHub pull request model."""

    __tablename__ = "pull_requests"

    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(Integer, unique=True, nullable=False, index=True)
    number = Column(Integer, nullable=False, index=True)
    title = Column(String(500), nullable=False, index=True)
    body = Column(Text, nullable=True)
    state = Column(String(50), nullable=False, index=True)  # open, closed, merged
    base_branch = Column(String(255), nullable=False)
    head_branch = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)

    # Metrics
    additions = Column(Integer, nullable=False, default=0)
    deletions = Column(Integer, nullable=False, default=0)
    changed_files = Column(Integer, nullable=False, default=0)
    commits_count = Column(Integer, nullable=False, default=0)
    comments_count = Column(Integer, nullable=False, default=0)
    review_comments_count = Column(Integer, nullable=False, default=0)

    # Time tracking
    created_at = Column(DateTime, nullable=False, index=True)
    updated_at = Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )
    closed_at = Column(DateTime, nullable=True)
    merged_at = Column(DateTime, nullable=True, index=True)

    # Foreign keys
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("github_users.id"), nullable=False)
    linked_issue_id = Column(Integer, ForeignKey("issues.id"), nullable=True)

    # Relationships
    repository = relationship("Repository", back_populates="pull_requests")
    author = relationship("GitHubUser", back_populates="pull_requests")
    linked_issue = relationship("Issue", back_populates="pull_requests")
    commits = relationship("Commit", back_populates="pull_request")

    @property
    def is_merged(self) -> bool:
        """Check if PR is merged."""
        return self.merged_at is not None

    @property
    def review_time_hours(self) -> Optional[float]:
        """Calculate time from creation to merge/close in hours."""
        end_time = self.merged_at or self.closed_at
        if end_time and self.created_at:
            delta = end_time - self.created_at
            return delta.total_seconds() / 3600
        return None

    @property
    def lines_changed(self) -> int:
        """Total lines changed (additions + deletions)."""
        return self.additions + self.deletions


class Commit(Base):
    """GitHub commit model."""

    __tablename__ = "commits"

    id = Column(Integer, primary_key=True, index=True)
    sha = Column(String(40), unique=True, nullable=False, index=True)
    message = Column(Text, nullable=False)
    url = Column(String(500), nullable=False)

    # Metrics
    additions = Column(Integer, nullable=False, default=0)
    deletions = Column(Integer, nullable=False, default=0)
    total_changes = Column(Integer, nullable=False, default=0)

    # Time tracking
    committed_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=func.now())

    # Foreign keys
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("github_users.id"), nullable=False)
    pull_request_id = Column(Integer, ForeignKey("pull_requests.id"), nullable=True)

    # Relationships
    repository = relationship("Repository", back_populates="commits")
    author = relationship("GitHubUser", back_populates="commits")
    pull_request = relationship("PullRequest", back_populates="commits")

    @property
    def lines_changed(self) -> int:
        """Total lines changed in this commit."""
        return self.additions + self.deletions
