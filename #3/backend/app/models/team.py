from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    Float,
    Enum as SqlEnum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum
from typing import Optional

from app.core.database import Base


class SeniorityLevel(str, Enum):
    """Enumeration for team member seniority levels."""

    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    PRINCIPAL = "principal"


class ExperienceLevel(str, Enum):
    """Enumeration for technology experience levels."""

    NOVICE = "novice"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class Team(Base):
    """Team model for storing team information."""

    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    # Team metrics
    average_velocity = Column(Float, nullable=True)  # Story points per sprint
    average_cycle_time_hours = Column(Float, nullable=True)
    estimation_accuracy_score = Column(Float, nullable=True)  # 0-1 scale

    # Time tracking
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    # Relationships
    members = relationship("TeamMember", back_populates="team")
    sprints = relationship("Sprint", back_populates="team")

    @property
    def current_size(self) -> int:
        """Get current active team size."""
        return len([m for m in self.members if m.is_active])

    @property
    def seniority_distribution(self) -> dict:
        """Get distribution of seniority levels in the team."""
        active_members = [m for m in self.members if m.is_active]
        distribution = {}
        for level in SeniorityLevel:
            count = len([m for m in active_members if m.seniority_level == level])
            distribution[level.value] = count
        return distribution


class TeamMember(Base):
    """Team member model for storing individual team member information."""

    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=True, unique=True, index=True)
    github_username = Column(String(255), nullable=True, index=True)

    # Member characteristics
    seniority_level = Column(
        SqlEnum(SeniorityLevel), nullable=False, default=SeniorityLevel.MID
    )
    years_of_experience = Column(Float, nullable=True)
    hourly_rate = Column(Float, nullable=True)  # For cost estimation
    is_active = Column(Boolean, nullable=False, default=True)

    # Performance metrics
    average_story_points_per_sprint = Column(Float, nullable=True)
    average_completion_time_hours = Column(Float, nullable=True)
    quality_score = Column(
        Float, nullable=True
    )  # Based on bug rates, code review feedback

    # Time tracking
    joined_team_at = Column(DateTime, nullable=False, default=func.now())
    left_team_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    # Foreign keys
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)

    # Relationships
    team = relationship("Team", back_populates="members")
    technology_experiences = relationship(
        "TechnologyExperience", back_populates="team_member"
    )

    @property
    def is_currently_active(self) -> bool:
        """Check if member is currently active in the team."""
        return self.is_active and self.left_team_at is None

    @property
    def tenure_months(self) -> Optional[float]:
        """Calculate tenure in the team in months."""
        if self.joined_team_at:
            end_date = self.left_team_at or datetime.utcnow()
            delta = end_date - self.joined_team_at
            return delta.days / 30.44  # Average days per month
        return None


class TechnologyExperience(Base):
    """Model for storing team member experience with specific technologies."""

    __tablename__ = "technology_experiences"

    id = Column(Integer, primary_key=True, index=True)
    technology_name = Column(String(255), nullable=False, index=True)
    category = Column(
        String(100), nullable=True
    )  # e.g., "language", "framework", "tool"

    experience_level = Column(
        SqlEnum(ExperienceLevel), nullable=False, default=ExperienceLevel.INTERMEDIATE
    )
    years_of_experience = Column(Float, nullable=True)
    last_used_date = Column(DateTime, nullable=True)
    proficiency_score = Column(Float, nullable=True)  # 0-100 scale

    # Additional context
    notes = Column(Text, nullable=True)
    is_primary_skill = Column(Boolean, nullable=False, default=False)

    # Time tracking
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    # Foreign keys
    team_member_id = Column(Integer, ForeignKey("team_members.id"), nullable=False)

    # Relationships
    team_member = relationship("TeamMember", back_populates="technology_experiences")

    @property
    def is_current_skill(self) -> bool:
        """Check if this is a current/recent skill."""
        if not self.last_used_date:
            return True  # Assume current if no date specified

        months_since_last_use = (datetime.utcnow() - self.last_used_date).days / 30.44
        return months_since_last_use <= 12  # Consider current if used within last year


class Sprint(Base):
    """Model for storing sprint information and team composition."""

    __tablename__ = "sprints"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Sprint timeline
    start_date = Column(DateTime, nullable=False, index=True)
    end_date = Column(DateTime, nullable=False, index=True)
    is_active = Column(Boolean, nullable=False, default=False)
    is_completed = Column(Boolean, nullable=False, default=False)

    # Sprint metrics
    planned_story_points = Column(Integer, nullable=True)
    completed_story_points = Column(Integer, nullable=True)
    planned_hours = Column(Float, nullable=True)
    actual_hours = Column(Float, nullable=True)

    # Team composition during this sprint
    team_size = Column(Integer, nullable=False, default=0)
    senior_count = Column(Integer, nullable=False, default=0)
    mid_count = Column(Integer, nullable=False, default=0)
    junior_count = Column(Integer, nullable=False, default=0)

    # Performance metrics
    velocity = Column(Float, nullable=True)  # Completed story points
    burndown_rate = Column(Float, nullable=True)  # Story points per day
    estimation_accuracy = Column(Float, nullable=True)  # Actual vs planned ratio

    # Time tracking
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    # Foreign keys
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)

    # Relationships
    team = relationship("Team", back_populates="sprints")

    @property
    def duration_days(self) -> int:
        """Calculate sprint duration in days."""
        return (self.end_date - self.start_date).days

    @property
    def completion_percentage(self) -> Optional[float]:
        """Calculate completion percentage based on story points."""
        if self.planned_story_points and self.planned_story_points > 0:
            completed = self.completed_story_points or 0
            return (completed / self.planned_story_points) * 100
        return None

    @property
    def hours_estimation_accuracy(self) -> Optional[float]:
        """Calculate estimation accuracy for hours."""
        if self.planned_hours and self.actual_hours:
            return min(self.planned_hours, self.actual_hours) / max(
                self.planned_hours, self.actual_hours
            )
        return None

    @property
    def story_points_estimation_accuracy(self) -> Optional[float]:
        """Calculate estimation accuracy for story points."""
        if self.planned_story_points and self.completed_story_points:
            return min(self.planned_story_points, self.completed_story_points) / max(
                self.planned_story_points, self.completed_story_points
            )
        return None
