from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.core.database import get_db
from app.models.github import Repository, Issue, PullRequest, Commit
from app.models.team import Team, TeamMember, Sprint
from app.models.prediction import (
    Prediction,
    PredictionModel,
    EstimationAccuracy,
    PredictionStatus,
)

router = APIRouter()


# Pydantic models for API responses
class TeamVelocityResponse(BaseModel):
    team_id: int
    team_name: str
    period_start: datetime
    period_end: datetime
    total_story_points_completed: Optional[int]
    total_hours_logged: Optional[float]
    velocity_per_day: Optional[float]
    estimation_accuracy: Optional[float]


class RepositoryInsightsResponse(BaseModel):
    repository_id: int
    repository_name: str
    total_issues: int
    open_issues: int
    closed_issues: int
    average_resolution_time_hours: Optional[float]
    most_common_labels: List[Dict[str, Any]]
    contributor_count: int


class PredictionAnalyticsResponse(BaseModel):
    total_predictions: int
    validated_predictions: int
    average_accuracy: Optional[float]
    accuracy_by_type: Dict[str, float]
    accuracy_trends: List[Dict[str, Any]]


@router.get("/teams/velocity", response_model=List[TeamVelocityResponse])
async def get_team_velocity_analytics(
    team_id: Optional[int] = Query(None),
    days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db),
):
    """
    Get team velocity analytics for the specified period.
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Build base query
    query = db.query(Team)

    if team_id:
        query = query.filter(Team.id == team_id)

    teams = query.filter(Team.is_active == True).all()

    if not teams:
        return []

    results = []

    for team in teams:
        # Get sprints in the period
        sprints = (
            db.query(Sprint)
            .filter(
                Sprint.team_id == team.id,
                Sprint.start_date >= start_date,
                Sprint.end_date <= end_date,
                Sprint.is_completed == True,
            )
            .all()
        )

        if not sprints:
            # Create entry with no data
            results.append(
                TeamVelocityResponse(
                    team_id=team.id,
                    team_name=team.name,
                    period_start=start_date,
                    period_end=end_date,
                    total_story_points_completed=None,
                    total_hours_logged=None,
                    velocity_per_day=None,
                    estimation_accuracy=None,
                )
            )
            continue

        # Calculate metrics
        total_story_points = sum(s.completed_story_points or 0 for s in sprints)
        total_hours = sum(s.actual_hours or 0 for s in sprints)

        # Calculate velocity per day
        total_sprint_days = sum(s.duration_days for s in sprints)
        velocity_per_day = (
            total_story_points / total_sprint_days if total_sprint_days > 0 else None
        )

        # Calculate average estimation accuracy
        accuracy_scores = [
            s.story_points_estimation_accuracy
            for s in sprints
            if s.story_points_estimation_accuracy is not None
        ]
        avg_accuracy = (
            sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else None
        )

        results.append(
            TeamVelocityResponse(
                team_id=team.id,
                team_name=team.name,
                period_start=start_date,
                period_end=end_date,
                total_story_points_completed=total_story_points
                if total_story_points > 0
                else None,
                total_hours_logged=total_hours if total_hours > 0 else None,
                velocity_per_day=velocity_per_day,
                estimation_accuracy=avg_accuracy,
            )
        )

    return results


@router.get("/repositories/insights", response_model=List[RepositoryInsightsResponse])
async def get_repository_insights(
    repository_id: Optional[int] = Query(None),
    days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db),
):
    """
    Get repository insights and analytics.
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Build base query
    query = db.query(Repository)

    if repository_id:
        query = query.filter(Repository.id == repository_id)

    repositories = query.all()

    if not repositories:
        return []

    results = []

    for repo in repositories:
        # Get issues in the period
        issues_query = db.query(Issue).filter(
            Issue.repository_id == repo.id, Issue.created_at >= start_date
        )

        total_issues = issues_query.count()
        open_issues = issues_query.filter(Issue.state == "open").count()
        closed_issues = issues_query.filter(Issue.state == "closed").count()

        # Calculate average resolution time
        closed_issues_with_time = issues_query.filter(
            Issue.state == "closed", Issue.closed_at.isnot(None)
        ).all()

        avg_resolution_time = None
        if closed_issues_with_time:
            resolution_times = [
                i.resolution_time_hours
                for i in closed_issues_with_time
                if i.resolution_time_hours is not None
            ]
            if resolution_times:
                avg_resolution_time = sum(resolution_times) / len(resolution_times)

        # Get most common labels (mock implementation)
        # In a real implementation, you'd parse the labels JSON field
        most_common_labels = [
            {"label": "bug", "count": 5},
            {"label": "enhancement", "count": 3},
            {"label": "documentation", "count": 2},
        ]

        # Count unique contributors
        contributor_count = (
            db.query(func.count(func.distinct(Issue.author_id)))
            .filter(Issue.repository_id == repo.id, Issue.created_at >= start_date)
            .scalar()
            or 0
        )

        results.append(
            RepositoryInsightsResponse(
                repository_id=repo.id,
                repository_name=repo.full_name,
                total_issues=total_issues,
                open_issues=open_issues,
                closed_issues=closed_issues,
                average_resolution_time_hours=avg_resolution_time,
                most_common_labels=most_common_labels,
                contributor_count=contributor_count,
            )
        )

    return results


@router.get("/predictions/analytics", response_model=PredictionAnalyticsResponse)
async def get_prediction_analytics(
    team_id: Optional[int] = Query(None),
    days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db),
):
    """
    Get prediction accuracy analytics.
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Build base query
    query = db.query(Prediction).filter(
        Prediction.created_at >= start_date, Prediction.created_at <= end_date
    )

    if team_id:
        query = query.filter(Prediction.team_id == team_id)

    all_predictions = query.all()
    validated_predictions = [
        p for p in all_predictions if p.status == PredictionStatus.VALIDATED
    ]

    total_predictions = len(all_predictions)
    validated_count = len(validated_predictions)

    # Calculate average accuracy
    accuracies = [
        p.accuracy_percentage
        for p in validated_predictions
        if p.accuracy_percentage is not None
    ]
    average_accuracy = sum(accuracies) / len(accuracies) if accuracies else None

    # Calculate accuracy by prediction type
    accuracy_by_type = {}
    for pred_type in ["story_points", "hours", "complexity", "risk_score"]:
        type_predictions = [
            p for p in validated_predictions if p.prediction_type.value == pred_type
        ]
        if type_predictions:
            type_accuracies = [
                p.accuracy_percentage
                for p in type_predictions
                if p.accuracy_percentage is not None
            ]
            if type_accuracies:
                accuracy_by_type[pred_type] = sum(type_accuracies) / len(
                    type_accuracies
                )

    # Calculate weekly accuracy trends
    accuracy_trends = []
    current_date = start_date
    while current_date < end_date:
        week_end = min(current_date + timedelta(days=7), end_date)

        week_predictions = [
            p for p in validated_predictions if current_date <= p.created_at < week_end
        ]

        if week_predictions:
            week_accuracies = [
                p.accuracy_percentage
                for p in week_predictions
                if p.accuracy_percentage is not None
            ]
            week_avg = (
                sum(week_accuracies) / len(week_accuracies) if week_accuracies else None
            )
        else:
            week_avg = None

        accuracy_trends.append(
            {
                "week_start": current_date.isoformat(),
                "week_end": week_end.isoformat(),
                "predictions_count": len(week_predictions),
                "average_accuracy": week_avg,
            }
        )

        current_date = week_end

    return PredictionAnalyticsResponse(
        total_predictions=total_predictions,
        validated_predictions=validated_count,
        average_accuracy=average_accuracy,
        accuracy_by_type=accuracy_by_type,
        accuracy_trends=accuracy_trends,
    )


@router.get("/dashboard/summary")
async def get_dashboard_summary(
    team_id: Optional[int] = Query(None),
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
):
    """
    Get summary data for the main dashboard.
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Team metrics
    team_query = db.query(Team)
    if team_id:
        team_query = team_query.filter(Team.id == team_id)

    active_teams = team_query.filter(Team.is_active == True).count()

    # Prediction metrics
    pred_query = db.query(Prediction).filter(Prediction.created_at >= start_date)
    if team_id:
        pred_query = pred_query.filter(Prediction.team_id == team_id)

    recent_predictions = pred_query.count()
    validated_predictions = pred_query.filter(
        Prediction.status == PredictionStatus.VALIDATED
    ).count()

    # Repository metrics
    repo_query = db.query(Repository)
    total_repositories = repo_query.count()

    # Issue metrics
    issue_query = db.query(Issue).filter(Issue.created_at >= start_date)
    recent_issues = issue_query.count()
    closed_issues = issue_query.filter(Issue.state == "closed").count()

    # Model metrics
    active_models = (
        db.query(PredictionModel).filter(PredictionModel.status == "active").count()
    )

    return {
        "period_days": days,
        "period_start": start_date.isoformat(),
        "period_end": end_date.isoformat(),
        "team_metrics": {
            "active_teams": active_teams,
            "total_members": db.query(TeamMember)
            .filter(TeamMember.is_active == True)
            .count(),
        },
        "prediction_metrics": {
            "recent_predictions": recent_predictions,
            "validated_predictions": validated_predictions,
            "validation_rate": (validated_predictions / recent_predictions * 100)
            if recent_predictions > 0
            else 0,
        },
        "repository_metrics": {
            "total_repositories": total_repositories,
            "recent_issues": recent_issues,
            "issues_closed": closed_issues,
            "close_rate": (closed_issues / recent_issues * 100)
            if recent_issues > 0
            else 0,
        },
        "model_metrics": {
            "active_models": active_models,
            "total_models": db.query(PredictionModel).count(),
        },
    }


@router.get("/teams/{team_id}/performance")
async def get_team_performance(
    team_id: int,
    days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db),
):
    """
    Get detailed performance analytics for a specific team.
    """
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Get team predictions in period
    predictions = (
        db.query(Prediction)
        .filter(Prediction.team_id == team_id, Prediction.created_at >= start_date)
        .all()
    )

    validated_predictions = [
        p for p in predictions if p.status == PredictionStatus.VALIDATED
    ]

    # Calculate performance metrics
    total_predictions = len(predictions)
    validation_rate = (
        (len(validated_predictions) / total_predictions * 100)
        if total_predictions > 0
        else 0
    )

    # Accuracy metrics
    accuracies = [
        p.accuracy_percentage
        for p in validated_predictions
        if p.accuracy_percentage is not None
    ]
    avg_accuracy = sum(accuracies) / len(accuracies) if accuracies else None

    # Prediction distribution by type
    prediction_distribution = {}
    for pred in predictions:
        pred_type = pred.prediction_type.value
        if pred_type not in prediction_distribution:
            prediction_distribution[pred_type] = 0
        prediction_distribution[pred_type] += 1

    # Get sprint data
    sprints = (
        db.query(Sprint)
        .filter(Sprint.team_id == team_id, Sprint.start_date >= start_date)
        .all()
    )

    sprint_metrics = []
    for sprint in sprints:
        sprint_metrics.append(
            {
                "sprint_name": sprint.name,
                "start_date": sprint.start_date.isoformat(),
                "end_date": sprint.end_date.isoformat(),
                "planned_story_points": sprint.planned_story_points,
                "completed_story_points": sprint.completed_story_points,
                "completion_percentage": sprint.completion_percentage,
                "velocity": sprint.velocity,
                "estimation_accuracy": sprint.story_points_estimation_accuracy,
            }
        )

    return {
        "team_name": team.name,
        "team_id": team_id,
        "period_start": start_date.isoformat(),
        "period_end": end_date.isoformat(),
        "prediction_metrics": {
            "total_predictions": total_predictions,
            "validated_predictions": len(validated_predictions),
            "validation_rate": validation_rate,
            "average_accuracy": avg_accuracy,
            "prediction_distribution": prediction_distribution,
        },
        "sprint_metrics": sprint_metrics,
        "team_composition": {
            "total_members": team.current_size,
            "seniority_distribution": team.seniority_distribution,
        },
    }


@router.get("/health")
async def analytics_health_check():
    """
    Health check for analytics API.
    """
    return {"status": "healthy", "service": "analytics"}
