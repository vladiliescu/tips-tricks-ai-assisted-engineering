"""
Database models package.

This package contains all SQLAlchemy models for the predictive analytics application.
Models are organized by domain:
- github: GitHub-related entities (repositories, issues, pull requests, commits)
- team: Team and member-related entities
- prediction: Prediction and estimation-related entities
"""

from app.models.github import (
    Repository,
    Issue,
    PullRequest,
    Commit,
    GitHubUser,
)

from app.models.team import (
    Team,
    TeamMember,
    TechnologyExperience,
    Sprint,
)

from app.models.prediction import (
    Prediction,
    PredictionModel,
    EstimationAccuracy,
    TaskFeature,
)

__all__ = [
    # GitHub models
    "Repository",
    "Issue",
    "PullRequest",
    "Commit",
    "GitHubUser",
    # Team models
    "Team",
    "TeamMember",
    "TechnologyExperience",
    "Sprint",
    # Prediction models
    "Prediction",
    "PredictionModel",
    "EstimationAccuracy",
    "TaskFeature",
]
