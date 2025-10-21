from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import httpx

from app.core.database import get_db
from app.core.config import settings
from app.models.github import Repository, Issue, PullRequest, Commit, GitHubUser

router = APIRouter()


# Pydantic models for API responses
from pydantic import BaseModel


class RepositoryResponse(BaseModel):
    id: int
    github_id: int
    name: str
    full_name: str
    description: Optional[str]
    url: str
    language: Optional[str]
    stargazers_count: int
    forks_count: int
    open_issues_count: int
    is_private: bool
    created_at: datetime
    last_synced_at: Optional[datetime]

    class Config:
        from_attributes = True


class IssueResponse(BaseModel):
    id: int
    github_id: int
    number: int
    title: str
    state: str
    labels: Optional[str]
    created_at: datetime
    closed_at: Optional[datetime]
    estimated_hours: Optional[float]
    actual_hours: Optional[float]
    story_points: Optional[int]
    resolution_time_hours: Optional[float]

    class Config:
        from_attributes = True


class SyncRequest(BaseModel):
    repository_full_name: str
    github_token: Optional[str] = None


class SyncResponse(BaseModel):
    message: str
    repository_id: int
    issues_synced: int
    pull_requests_synced: int
    commits_synced: int


@router.get("/repositories", response_model=List[RepositoryResponse])
async def list_repositories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """
    List all repositories in the database.
    """
    repositories = db.query(Repository).offset(skip).limit(limit).all()
    return repositories


@router.get("/repositories/{repo_id}", response_model=RepositoryResponse)
async def get_repository(repo_id: int, db: Session = Depends(get_db)):
    """
    Get a specific repository by ID.
    """
    repository = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")
    return repository


@router.get("/repositories/{repo_id}/issues", response_model=List[IssueResponse])
async def list_repository_issues(
    repo_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    state: Optional[str] = Query(None, regex="^(open|closed|all)$"),
    db: Session = Depends(get_db),
):
    """
    List issues for a specific repository.
    """
    # Verify repository exists
    repository = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")

    # Build query
    query = db.query(Issue).filter(Issue.repository_id == repo_id)

    if state and state != "all":
        query = query.filter(Issue.state == state)

    issues = query.offset(skip).limit(limit).all()
    return issues


@router.post("/repositories/sync", response_model=SyncResponse)
async def sync_repository(sync_request: SyncRequest, db: Session = Depends(get_db)):
    """
    Sync a repository from GitHub API.
    This is a minimal implementation - in a real app, this would:
    1. Fetch data from GitHub API
    2. Parse and store in database
    3. Handle rate limiting and errors
    """
    # Use provided token or default from settings
    token = sync_request.github_token or settings.github_token
    if not token:
        raise HTTPException(status_code=400, detail="GitHub token is required")

    try:
        # This is a placeholder implementation
        # In reality, you would call GitHub API here
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github.v3+json",
            }

            # Simulate API call (commented out for minimal implementation)
            # repo_response = await client.get(
            #     f"{settings.github_api_url}/repos/{sync_request.repository_full_name}",
            #     headers=headers
            # )

            # For now, create a mock repository entry
            existing_repo = (
                db.query(Repository)
                .filter(Repository.full_name == sync_request.repository_full_name)
                .first()
            )

            if existing_repo:
                existing_repo.last_synced_at = datetime.utcnow()
                db.commit()
                repo_id = existing_repo.id
            else:
                # Create mock repository
                new_repo = Repository(
                    github_id=12345,  # Mock GitHub ID
                    name=sync_request.repository_full_name.split("/")[-1],
                    full_name=sync_request.repository_full_name,
                    description=f"Mock repository for {sync_request.repository_full_name}",
                    url=f"https://github.com/{sync_request.repository_full_name}",
                    clone_url=f"https://github.com/{sync_request.repository_full_name}.git",
                    default_branch="main",
                    language="Python",
                    size=1000,
                    stargazers_count=10,
                    forks_count=5,
                    open_issues_count=3,
                    is_private=False,
                    is_fork=False,
                    owner_id=1,  # Mock owner ID
                    created_at=datetime.utcnow(),
                    last_synced_at=datetime.utcnow(),
                )

                # Need to create a mock user first
                mock_user = (
                    db.query(GitHubUser).filter(GitHubUser.login == "mockuser").first()
                )
                if not mock_user:
                    mock_user = GitHubUser(
                        github_id=1,
                        login="mockuser",
                        name="Mock User",
                        email="mock@example.com",
                        type="User",
                        created_at=datetime.utcnow(),
                    )
                    db.add(mock_user)
                    db.commit()
                    db.refresh(mock_user)

                new_repo.owner_id = mock_user.id
                db.add(new_repo)
                db.commit()
                db.refresh(new_repo)
                repo_id = new_repo.id

            return SyncResponse(
                message=f"Repository {sync_request.repository_full_name} synced successfully",
                repository_id=repo_id,
                issues_synced=0,  # Mock values
                pull_requests_synced=0,
                commits_synced=0,
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@router.get("/repositories/{repo_id}/analytics")
async def get_repository_analytics(repo_id: int, db: Session = Depends(get_db)):
    """
    Get analytics for a specific repository.
    """
    repository = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")

    # Calculate basic analytics
    total_issues = db.query(Issue).filter(Issue.repository_id == repo_id).count()
    open_issues = (
        db.query(Issue)
        .filter(Issue.repository_id == repo_id, Issue.state == "open")
        .count()
    )
    closed_issues = total_issues - open_issues

    # Calculate average resolution time for closed issues
    closed_issues_with_time = (
        db.query(Issue)
        .filter(
            Issue.repository_id == repo_id,
            Issue.state == "closed",
            Issue.created_at.isnot(None),
            Issue.closed_at.isnot(None),
        )
        .all()
    )

    avg_resolution_time = None
    if closed_issues_with_time:
        total_resolution_time = sum(
            issue.resolution_time_hours
            for issue in closed_issues_with_time
            if issue.resolution_time_hours is not None
        )
        if total_resolution_time > 0:
            avg_resolution_time = total_resolution_time / len(closed_issues_with_time)

    return {
        "repository_name": repository.full_name,
        "total_issues": total_issues,
        "open_issues": open_issues,
        "closed_issues": closed_issues,
        "open_percentage": (open_issues / total_issues * 100)
        if total_issues > 0
        else 0,
        "average_resolution_time_hours": avg_resolution_time,
        "last_synced_at": repository.last_synced_at,
    }


@router.get("/health")
async def github_health_check():
    """
    Health check for GitHub API integration.
    """
    return {
        "status": "healthy",
        "github_api_url": settings.github_api_url,
        "has_token": bool(settings.github_token),
    }
