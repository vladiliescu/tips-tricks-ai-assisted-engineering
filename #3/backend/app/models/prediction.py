from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    Float,
    JSON,
    Enum as SqlEnum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any

from app.core.database import Base


class PredictionType(str, Enum):
    """Enumeration for prediction types."""

    STORY_POINTS = "story_points"
    HOURS = "hours"
    COMPLEXITY = "complexity"
    RISK_SCORE = "risk_score"


class ModelStatus(str, Enum):
    """Enumeration for model status."""

    TRAINING = "training"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    FAILED = "failed"


class PredictionStatus(str, Enum):
    """Enumeration for prediction status."""

    PENDING = "pending"
    COMPLETED = "completed"
    VALIDATED = "validated"
    FAILED = "failed"


class PredictionModel(Base):
    """Model for storing ML model metadata and versions."""

    __tablename__ = "prediction_models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    version = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Model characteristics
    model_type = Column(
        String(100), nullable=False
    )  # e.g., "linear_regression", "random_forest"
    prediction_type = Column(SqlEnum(PredictionType), nullable=False)
    status = Column(SqlEnum(ModelStatus), nullable=False, default=ModelStatus.TRAINING)

    # Model performance metrics
    accuracy_score = Column(Float, nullable=True)
    mae = Column(Float, nullable=True)  # Mean Absolute Error
    mse = Column(Float, nullable=True)  # Mean Squared Error
    r2_score = Column(Float, nullable=True)  # R-squared score
    cross_validation_score = Column(Float, nullable=True)

    # Model configuration
    hyperparameters = Column(JSON, nullable=True)
    feature_columns = Column(JSON, nullable=True)
    training_data_size = Column(Integer, nullable=True)
    validation_data_size = Column(Integer, nullable=True)

    # Model artifacts
    model_file_path = Column(String(500), nullable=True)
    feature_scaler_path = Column(String(500), nullable=True)
    model_artifacts = Column(JSON, nullable=True)

    # Time tracking
    training_started_at = Column(DateTime, nullable=True)
    training_completed_at = Column(DateTime, nullable=True)
    deployed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    # Relationships
    predictions = relationship("Prediction", back_populates="model")

    @property
    def training_duration_minutes(self) -> Optional[float]:
        """Calculate training duration in minutes."""
        if self.training_started_at and self.training_completed_at:
            delta = self.training_completed_at - self.training_started_at
            return delta.total_seconds() / 60
        return None

    @property
    def is_active(self) -> bool:
        """Check if model is currently active."""
        return self.status == ModelStatus.ACTIVE

    @property
    def performance_summary(self) -> Dict[str, Any]:
        """Get a summary of model performance metrics."""
        return {
            "accuracy_score": self.accuracy_score,
            "mae": self.mae,
            "mse": self.mse,
            "r2_score": self.r2_score,
            "cross_validation_score": self.cross_validation_score,
            "training_data_size": self.training_data_size,
        }


class Prediction(Base):
    """Model for storing predictions made by the system."""

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)

    # Task information
    task_title = Column(String(500), nullable=False, index=True)
    task_description = Column(Text, nullable=True)
    task_type = Column(
        String(100), nullable=True
    )  # e.g., "feature", "bug", "improvement"

    # Input features used for prediction
    input_features = Column(JSON, nullable=False)
    feature_hash = Column(String(64), nullable=True, index=True)  # For deduplication

    # Prediction results
    prediction_type = Column(SqlEnum(PredictionType), nullable=False)
    predicted_value = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=True)  # 0-1 scale
    confidence_interval_lower = Column(Float, nullable=True)
    confidence_interval_upper = Column(Float, nullable=True)

    # Additional predictions (if multiple types predicted at once)
    secondary_predictions = Column(JSON, nullable=True)

    # Validation data (filled when actual values become available)
    actual_value = Column(Float, nullable=True)
    validation_date = Column(DateTime, nullable=True)
    validation_source = Column(
        String(100), nullable=True
    )  # e.g., "manual", "github", "jira"

    # Status and metadata
    status = Column(
        SqlEnum(PredictionStatus), nullable=False, default=PredictionStatus.PENDING
    )
    prediction_context = Column(JSON, nullable=True)  # Team info, sprint info, etc.
    notes = Column(Text, nullable=True)

    # Time tracking
    created_at = Column(DateTime, nullable=False, default=func.now(), index=True)
    updated_at = Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    # Foreign keys
    model_id = Column(Integer, ForeignKey("prediction_models.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=True)
    issue_id = Column(Integer, ForeignKey("issues.id"), nullable=True)

    # Relationships
    model = relationship("PredictionModel", back_populates="predictions")
    # Note: team, repository, issue relationships would be added when importing those models

    @property
    def is_validated(self) -> bool:
        """Check if prediction has been validated with actual values."""
        return self.actual_value is not None and self.validation_date is not None

    @property
    def accuracy_percentage(self) -> Optional[float]:
        """Calculate prediction accuracy if actual value is available."""
        if not self.is_validated:
            return None

        if self.actual_value == 0:
            return 100.0 if self.predicted_value == 0 else 0.0

        error_rate = abs(self.predicted_value - self.actual_value) / abs(
            self.actual_value
        )
        return max(0, (1 - error_rate) * 100)

    @property
    def absolute_error(self) -> Optional[float]:
        """Calculate absolute error if actual value is available."""
        if not self.is_validated:
            return None
        return abs(self.predicted_value - self.actual_value)

    @property
    def relative_error(self) -> Optional[float]:
        """Calculate relative error percentage if actual value is available."""
        if not self.is_validated or self.actual_value == 0:
            return None
        return ((self.predicted_value - self.actual_value) / self.actual_value) * 100


class EstimationAccuracy(Base):
    """Model for tracking estimation accuracy over time and by different dimensions."""

    __tablename__ = "estimation_accuracy"

    id = Column(Integer, primary_key=True, index=True)

    # Grouping dimensions
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    model_id = Column(Integer, ForeignKey("prediction_models.id"), nullable=True)
    prediction_type = Column(SqlEnum(PredictionType), nullable=False)
    time_period = Column(String(50), nullable=False)  # e.g., "2024-01", "Q1-2024"
    task_type = Column(String(100), nullable=True)

    # Accuracy metrics
    total_predictions = Column(Integer, nullable=False, default=0)
    validated_predictions = Column(Integer, nullable=False, default=0)
    average_accuracy_percentage = Column(Float, nullable=True)
    median_accuracy_percentage = Column(Float, nullable=True)
    mae = Column(Float, nullable=True)  # Mean Absolute Error
    mse = Column(Float, nullable=True)  # Mean Squared Error

    # Distribution metrics
    predictions_within_10_percent = Column(Integer, nullable=False, default=0)
    predictions_within_25_percent = Column(Integer, nullable=False, default=0)
    predictions_within_50_percent = Column(Integer, nullable=False, default=0)

    # Bias analysis
    average_overestimation_percentage = Column(Float, nullable=True)
    average_underestimation_percentage = Column(Float, nullable=True)
    overestimation_count = Column(Integer, nullable=False, default=0)
    underestimation_count = Column(Integer, nullable=False, default=0)

    # Time tracking
    calculated_at = Column(DateTime, nullable=False, default=func.now())
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)

    @property
    def validation_rate(self) -> float:
        """Calculate the percentage of predictions that have been validated."""
        if self.total_predictions == 0:
            return 0.0
        return (self.validated_predictions / self.total_predictions) * 100

    @property
    def accuracy_within_25_percent_rate(self) -> float:
        """Calculate the percentage of predictions within 25% accuracy."""
        if self.validated_predictions == 0:
            return 0.0
        return (self.predictions_within_25_percent / self.validated_predictions) * 100


class TaskFeature(Base):
    """Model for storing extracted features from tasks for ML training."""

    __tablename__ = "task_features"

    id = Column(Integer, primary_key=True, index=True)

    # Task identification
    task_source = Column(String(50), nullable=False)  # "github", "jira", "manual"
    task_source_id = Column(String(255), nullable=False)  # External ID
    task_title = Column(String(500), nullable=False)
    task_description = Column(Text, nullable=True)

    # Text-based features
    title_word_count = Column(Integer, nullable=True)
    description_word_count = Column(Integer, nullable=True)
    title_complexity_score = Column(Float, nullable=True)
    description_complexity_score = Column(Float, nullable=True)

    # Categorical features
    task_type = Column(String(100), nullable=True)
    priority_level = Column(String(50), nullable=True)
    component = Column(String(255), nullable=True)
    labels = Column(JSON, nullable=True)

    # Historical features
    similar_task_avg_hours = Column(Float, nullable=True)
    similar_task_avg_story_points = Column(Float, nullable=True)
    assignee_avg_velocity = Column(Float, nullable=True)
    team_avg_velocity = Column(Float, nullable=True)

    # Complexity indicators
    has_external_dependencies = Column(Boolean, nullable=False, default=False)
    requires_research = Column(Boolean, nullable=False, default=False)
    involves_new_technology = Column(Boolean, nullable=False, default=False)
    affects_multiple_components = Column(Boolean, nullable=False, default=False)

    # Context features
    team_size_at_time = Column(Integer, nullable=True)
    team_seniority_avg = Column(Float, nullable=True)
    sprint_capacity_percentage = Column(Float, nullable=True)

    # Target variables
    actual_hours = Column(Float, nullable=True)
    actual_story_points = Column(Integer, nullable=True)
    completion_date = Column(DateTime, nullable=True)

    # Feature processing metadata
    feature_vector = Column(JSON, nullable=True)  # Processed features for ML
    feature_version = Column(String(50), nullable=True)

    # Time tracking
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    # Foreign keys
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=True)
    issue_id = Column(Integer, ForeignKey("issues.id"), nullable=True)

    @property
    def has_completion_data(self) -> bool:
        """Check if task has completion data for training."""
        return self.completion_date is not None and (
            self.actual_hours is not None or self.actual_story_points is not None
        )

    @property
    def complexity_indicators_count(self) -> int:
        """Count how many complexity indicators are true."""
        indicators = [
            self.has_external_dependencies,
            self.requires_research,
            self.involves_new_technology,
            self.affects_multiple_components,
        ]
        return sum(1 for indicator in indicators if indicator)
