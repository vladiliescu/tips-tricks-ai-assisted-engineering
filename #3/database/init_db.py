#!/usr/bin/env python3
"""
Database initialization script for GitHub Predictive Analytics.

This script creates the database tables and optionally seeds them with sample data.
Run this script before starting the application for the first time.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the path so we can import our modules
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.core.database import Base, engine, get_database_session
from app.core.config import settings
from app.models.github import GitHubUser, Repository, Issue, PullRequest, Commit
from app.models.team import (
    Team,
    TeamMember,
    TechnologyExperience,
    Sprint,
    SeniorityLevel,
    ExperienceLevel,
)
from app.models.prediction import (
    PredictionModel,
    Prediction,
    EstimationAccuracy,
    TaskFeature,
    PredictionType,
    ModelStatus,
    PredictionStatus,
)
from datetime import datetime, timedelta
import json


def create_tables():
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")


def seed_sample_data():
    """Seed the database with sample data for testing and development."""
    print("Seeding sample data...")

    db = get_database_session()

    try:
        # Create sample GitHub users
        print("Creating sample GitHub users...")
        users = [
            GitHubUser(
                github_id=1,
                login="alice-dev",
                name="Alice Johnson",
                email="alice@example.com",
                avatar_url="https://avatars.githubusercontent.com/u/1",
                type="User",
                created_at=datetime.utcnow() - timedelta(days=365),
            ),
            GitHubUser(
                github_id=2,
                login="bob-engineer",
                name="Bob Smith",
                email="bob@example.com",
                avatar_url="https://avatars.githubusercontent.com/u/2",
                type="User",
                created_at=datetime.utcnow() - timedelta(days=300),
            ),
            GitHubUser(
                github_id=3,
                login="carol-lead",
                name="Carol Williams",
                email="carol@example.com",
                avatar_url="https://avatars.githubusercontent.com/u/3",
                type="User",
                created_at=datetime.utcnow() - timedelta(days=400),
            ),
        ]

        for user in users:
            db.add(user)
        db.commit()

        # Create sample repositories
        print("Creating sample repositories...")
        repositories = [
            Repository(
                github_id=101,
                name="web-app",
                full_name="company/web-app",
                description="Main web application for customer portal",
                url="https://github.com/company/web-app",
                clone_url="https://github.com/company/web-app.git",
                default_branch="main",
                language="TypeScript",
                size=15420,
                stargazers_count=45,
                forks_count=8,
                open_issues_count=12,
                is_private=True,
                is_fork=False,
                owner_id=1,
                created_at=datetime.utcnow() - timedelta(days=200),
                last_synced_at=datetime.utcnow() - timedelta(hours=2),
            ),
            Repository(
                github_id=102,
                name="api-service",
                full_name="company/api-service",
                description="REST API backend service",
                url="https://github.com/company/api-service",
                clone_url="https://github.com/company/api-service.git",
                default_branch="main",
                language="Python",
                size=8930,
                stargazers_count=23,
                forks_count=4,
                open_issues_count=7,
                is_private=True,
                is_fork=False,
                owner_id=2,
                created_at=datetime.utcnow() - timedelta(days=180),
                last_synced_at=datetime.utcnow() - timedelta(hours=1),
            ),
        ]

        for repo in repositories:
            db.add(repo)
        db.commit()

        # Create sample teams
        print("Creating sample teams...")
        teams = [
            Team(
                name="Frontend Team",
                description="Responsible for user interface and user experience",
                is_active=True,
                average_velocity=28.5,
                average_cycle_time_hours=72.4,
                estimation_accuracy_score=0.75,
            ),
            Team(
                name="Backend Team",
                description="API development and infrastructure",
                is_active=True,
                average_velocity=32.1,
                average_cycle_time_hours=64.2,
                estimation_accuracy_score=0.82,
            ),
            Team(
                name="DevOps Team",
                description="Infrastructure, deployment, and monitoring",
                is_active=True,
                average_velocity=18.7,
                average_cycle_time_hours=96.8,
                estimation_accuracy_score=0.68,
            ),
        ]

        for team in teams:
            db.add(team)
        db.commit()

        # Create sample team members
        print("Creating sample team members...")
        members = [
            # Frontend Team
            TeamMember(
                name="Alice Johnson",
                email="alice@example.com",
                github_username="alice-dev",
                seniority_level=SeniorityLevel.SENIOR,
                years_of_experience=6.5,
                hourly_rate=85.0,
                is_active=True,
                team_id=1,
                average_story_points_per_sprint=12.3,
                average_completion_time_hours=18.5,
                quality_score=0.92,
            ),
            TeamMember(
                name="David Chen",
                email="david@example.com",
                github_username="david-frontend",
                seniority_level=SeniorityLevel.MID,
                years_of_experience=3.2,
                hourly_rate=65.0,
                is_active=True,
                team_id=1,
                average_story_points_per_sprint=8.7,
                average_completion_time_hours=24.2,
                quality_score=0.85,
            ),
            # Backend Team
            TeamMember(
                name="Bob Smith",
                email="bob@example.com",
                github_username="bob-engineer",
                seniority_level=SeniorityLevel.LEAD,
                years_of_experience=8.1,
                hourly_rate=95.0,
                is_active=True,
                team_id=2,
                average_story_points_per_sprint=15.2,
                average_completion_time_hours=16.8,
                quality_score=0.94,
            ),
            TeamMember(
                name="Sarah Martinez",
                email="sarah@example.com",
                github_username="sarah-backend",
                seniority_level=SeniorityLevel.SENIOR,
                years_of_experience=5.8,
                hourly_rate=80.0,
                is_active=True,
                team_id=2,
                average_story_points_per_sprint=11.9,
                average_completion_time_hours=20.3,
                quality_score=0.88,
            ),
            # DevOps Team
            TeamMember(
                name="Carol Williams",
                email="carol@example.com",
                github_username="carol-lead",
                seniority_level=SeniorityLevel.PRINCIPAL,
                years_of_experience=12.3,
                hourly_rate=120.0,
                is_active=True,
                team_id=3,
                average_story_points_per_sprint=9.4,
                average_completion_time_hours=32.1,
                quality_score=0.96,
            ),
        ]

        for member in members:
            db.add(member)
        db.commit()

        # Create sample technology experiences
        print("Creating sample technology experiences...")
        tech_experiences = [
            # Alice - Frontend
            TechnologyExperience(
                technology_name="React",
                category="framework",
                experience_level=ExperienceLevel.EXPERT,
                years_of_experience=4.5,
                proficiency_score=95.0,
                is_primary_skill=True,
                team_member_id=1,
            ),
            TechnologyExperience(
                technology_name="TypeScript",
                category="language",
                experience_level=ExperienceLevel.ADVANCED,
                years_of_experience=3.8,
                proficiency_score=88.0,
                is_primary_skill=True,
                team_member_id=1,
            ),
            # Bob - Backend
            TechnologyExperience(
                technology_name="Python",
                category="language",
                experience_level=ExperienceLevel.EXPERT,
                years_of_experience=7.2,
                proficiency_score=96.0,
                is_primary_skill=True,
                team_member_id=3,
            ),
            TechnologyExperience(
                technology_name="FastAPI",
                category="framework",
                experience_level=ExperienceLevel.ADVANCED,
                years_of_experience=2.1,
                proficiency_score=85.0,
                is_primary_skill=True,
                team_member_id=3,
            ),
        ]

        for tech in tech_experiences:
            db.add(tech)
        db.commit()

        # Create sample prediction models
        print("Creating sample prediction models...")
        models = [
            PredictionModel(
                name="Story Points Estimator v1",
                version="1.0",
                description="Random Forest model for story point estimation",
                model_type="random_forest",
                prediction_type=PredictionType.STORY_POINTS,
                status=ModelStatus.ACTIVE,
                accuracy_score=0.78,
                mae=1.2,
                mse=2.1,
                r2_score=0.65,
                cross_validation_score=0.72,
                hyperparameters=json.dumps(
                    {"n_estimators": 100, "max_depth": 10, "min_samples_split": 5}
                ),
                feature_columns=json.dumps(
                    [
                        "title_word_count",
                        "description_word_count",
                        "team_size",
                        "avg_seniority",
                        "similar_tasks_avg",
                    ]
                ),
                training_data_size=450,
                validation_data_size=112,
                training_started_at=datetime.utcnow() - timedelta(days=7),
                training_completed_at=datetime.utcnow() - timedelta(days=6),
                deployed_at=datetime.utcnow() - timedelta(days=5),
            ),
            PredictionModel(
                name="Hours Estimator v1",
                version="1.0",
                description="Linear regression model for hour estimation",
                model_type="linear_regression",
                prediction_type=PredictionType.HOURS,
                status=ModelStatus.ACTIVE,
                accuracy_score=0.71,
                mae=4.8,
                mse=18.6,
                r2_score=0.58,
                cross_validation_score=0.66,
                training_data_size=380,
                validation_data_size=95,
                training_started_at=datetime.utcnow() - timedelta(days=5),
                training_completed_at=datetime.utcnow() - timedelta(days=4),
                deployed_at=datetime.utcnow() - timedelta(days=3),
            ),
        ]

        for model in models:
            db.add(model)
        db.commit()

        # Create sample issues
        print("Creating sample issues...")
        issues = [
            Issue(
                github_id=1001,
                number=1,
                title="Implement user authentication system",
                body="Need to add login/logout functionality with JWT tokens",
                state="closed",
                labels='["enhancement", "authentication", "security"]',
                assignees='["alice-dev"]',
                url="https://github.com/company/web-app/issues/1",
                created_at=datetime.utcnow() - timedelta(days=15),
                closed_at=datetime.utcnow() - timedelta(days=8),
                estimated_hours=24.0,
                actual_hours=28.5,
                story_points=8,
                complexity_score=7.2,
                repository_id=1,
                author_id=1,
            ),
            Issue(
                github_id=1002,
                number=2,
                title="Add pagination to user list",
                body="The user list page is slow when there are many users",
                state="open",
                labels='["performance", "frontend"]',
                assignees='["david-frontend"]',
                url="https://github.com/company/web-app/issues/2",
                created_at=datetime.utcnow() - timedelta(days=3),
                estimated_hours=6.0,
                story_points=3,
                complexity_score=4.1,
                repository_id=1,
                author_id=2,
            ),
        ]

        for issue in issues:
            db.add(issue)
        db.commit()

        # Create sample predictions
        print("Creating sample predictions...")
        predictions = [
            Prediction(
                task_title="Redesign dashboard layout",
                task_description="Update the main dashboard with new metrics and improved UX",
                task_type="enhancement",
                input_features=json.dumps(
                    {
                        "title_word_count": 3,
                        "description_word_count": 12,
                        "team_size": 2,
                        "avg_seniority": 4.2,
                        "similar_tasks_avg": 5.8,
                    }
                ),
                prediction_type=PredictionType.STORY_POINTS,
                predicted_value=5.0,
                confidence_score=0.82,
                confidence_interval_lower=4.0,
                confidence_interval_upper=7.0,
                status=PredictionStatus.COMPLETED,
                prediction_context=json.dumps(
                    {"sprint": "Sprint 24", "priority": "high"}
                ),
                model_id=1,
                team_id=1,
                repository_id=1,
                created_at=datetime.utcnow() - timedelta(days=2),
            ),
            Prediction(
                task_title="Optimize database queries",
                task_description="Improve performance of user data queries in the API",
                task_type="performance",
                input_features=json.dumps(
                    {
                        "title_word_count": 3,
                        "description_word_count": 10,
                        "team_size": 2,
                        "avg_seniority": 5.1,
                        "similar_tasks_avg": 8.2,
                    }
                ),
                prediction_type=PredictionType.HOURS,
                predicted_value=12.5,
                confidence_score=0.75,
                confidence_interval_lower=9.0,
                confidence_interval_upper=16.0,
                actual_value=14.2,
                validation_date=datetime.utcnow() - timedelta(hours=6),
                validation_source="manual",
                status=PredictionStatus.VALIDATED,
                model_id=2,
                team_id=2,
                repository_id=2,
                created_at=datetime.utcnow() - timedelta(days=5),
            ),
        ]

        for prediction in predictions:
            db.add(prediction)
        db.commit()

        # Create sample sprints
        print("Creating sample sprints...")
        sprints = [
            Sprint(
                name="Sprint 23",
                description="Focus on user authentication and security",
                start_date=datetime.utcnow() - timedelta(days=28),
                end_date=datetime.utcnow() - timedelta(days=14),
                is_active=False,
                is_completed=True,
                planned_story_points=25,
                completed_story_points=23,
                planned_hours=120.0,
                actual_hours=128.5,
                team_size=2,
                senior_count=1,
                mid_count=1,
                junior_count=0,
                velocity=23.0,
                burndown_rate=1.6,
                estimation_accuracy=0.85,
                team_id=1,
            ),
            Sprint(
                name="Sprint 24",
                description="Performance improvements and bug fixes",
                start_date=datetime.utcnow() - timedelta(days=14),
                end_date=datetime.utcnow(),
                is_active=True,
                is_completed=False,
                planned_story_points=28,
                completed_story_points=18,
                planned_hours=140.0,
                actual_hours=95.2,
                team_size=2,
                senior_count=1,
                mid_count=1,
                junior_count=0,
                velocity=18.0,
                burndown_rate=1.8,
                team_id=1,
            ),
        ]

        for sprint in sprints:
            db.add(sprint)
        db.commit()

        print("✅ Sample data seeded successfully!")

    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """Main function to initialize the database."""
    print("🚀 GitHub Predictive Analytics - Database Initialization")
    print("=" * 60)

    # Check if database file already exists (for SQLite)
    if settings.database_url.startswith("sqlite"):
        db_path = settings.database_url.replace("sqlite:///", "")
        if os.path.exists(db_path):
            response = input(
                f"Database file '{db_path}' already exists. Recreate? (y/N): "
            )
            if response.lower() != "y":
                print("Initialization cancelled.")
                return
            else:
                os.remove(db_path)
                print(f"Removed existing database file: {db_path}")

    try:
        # Create tables
        create_tables()

        # Ask if user wants to seed sample data
        response = input(
            "Would you like to seed the database with sample data? (Y/n): "
        )
        if response.lower() != "n":
            seed_sample_data()

        print("\n🎉 Database initialization completed successfully!")
        print("\nYou can now start the backend server with:")
        print("  cd backend")
        print("  uvicorn app.main:app --reload")

    except Exception as e:
        print(f"\n❌ Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
