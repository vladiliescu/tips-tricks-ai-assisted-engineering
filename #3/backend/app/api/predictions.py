from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.models.prediction import (
    Prediction,
    PredictionModel,
    EstimationAccuracy,
    TaskFeature,
    PredictionType,
    PredictionStatus,
    ModelStatus,
)
from app.models.team import Team
from app.models.github import Repository, Issue

router = APIRouter()


# Pydantic models for API requests and responses
class PredictionRequest(BaseModel):
    task_title: str
    task_description: Optional[str] = None
    task_type: Optional[str] = None
    team_id: Optional[int] = None
    repository_id: Optional[int] = None
    prediction_type: PredictionType = PredictionType.STORY_POINTS
    context: Optional[Dict[str, Any]] = None


class PredictionResponse(BaseModel):
    id: int
    task_title: str
    task_description: Optional[str]
    prediction_type: PredictionType
    predicted_value: float
    confidence_score: Optional[float]
    confidence_interval_lower: Optional[float]
    confidence_interval_upper: Optional[float]
    status: PredictionStatus
    created_at: datetime
    model_id: int
    model_name: Optional[str] = None

    class Config:
        from_attributes = True


class ValidationRequest(BaseModel):
    actual_value: float
    validation_source: Optional[str] = "manual"
    notes: Optional[str] = None


class ModelResponse(BaseModel):
    id: int
    name: str
    version: str
    description: Optional[str]
    model_type: str
    prediction_type: PredictionType
    status: ModelStatus
    accuracy_score: Optional[float]
    mae: Optional[float]
    mse: Optional[float]
    r2_score: Optional[float]
    training_data_size: Optional[int]
    created_at: datetime
    deployed_at: Optional[datetime]

    class Config:
        from_attributes = True


class TaskFeatureRequest(BaseModel):
    task_source: str
    task_source_id: str
    task_title: str
    task_description: Optional[str] = None
    task_type: Optional[str] = None
    team_id: Optional[int] = None
    repository_id: Optional[int] = None
    actual_hours: Optional[float] = None
    actual_story_points: Optional[int] = None


@router.post("/predict", response_model=PredictionResponse)
async def create_prediction(
    prediction_request: PredictionRequest, db: Session = Depends(get_db)
):
    """
    Create a new prediction for a task.
    This is a minimal implementation that creates a mock prediction.
    In a real system, this would:
    1. Extract features from the task
    2. Load the appropriate ML model
    3. Make the prediction
    4. Store the result
    """
    # Verify team exists if provided
    if prediction_request.team_id:
        team = db.query(Team).filter(Team.id == prediction_request.team_id).first()
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

    # Verify repository exists if provided
    if prediction_request.repository_id:
        repository = (
            db.query(Repository)
            .filter(Repository.id == prediction_request.repository_id)
            .first()
        )
        if not repository:
            raise HTTPException(status_code=404, detail="Repository not found")

    # Get the active model for this prediction type
    model = (
        db.query(PredictionModel)
        .filter(
            PredictionModel.prediction_type == prediction_request.prediction_type,
            PredictionModel.status == ModelStatus.ACTIVE,
        )
        .first()
    )

    if not model:
        # Create a default mock model if none exists
        model = PredictionModel(
            name="Default Mock Model",
            version="1.0",
            description="Default model for testing",
            model_type="mock_estimator",
            prediction_type=prediction_request.prediction_type,
            status=ModelStatus.ACTIVE,
            accuracy_score=0.75,
            mae=2.5,
            r2_score=0.60,
            training_data_size=100,
        )
        db.add(model)
        db.commit()
        db.refresh(model)

    # Mock prediction logic
    # In a real implementation, this would extract features and use ML model
    task_complexity = len(prediction_request.task_title.split()) + (
        len(prediction_request.task_description.split())
        if prediction_request.task_description
        else 0
    )

    base_prediction = task_complexity * 0.5
    if prediction_request.prediction_type == PredictionType.STORY_POINTS:
        predicted_value = max(1, min(13, round(base_prediction)))  # Cap at 1-13 points
    else:  # Hours
        predicted_value = max(0.5, base_prediction * 2)  # Convert to hours

    confidence_score = 0.7 + (task_complexity / 100)  # Mock confidence
    confidence_score = min(0.95, confidence_score)

    # Create prediction record
    prediction = Prediction(
        task_title=prediction_request.task_title,
        task_description=prediction_request.task_description,
        task_type=prediction_request.task_type,
        input_features={
            "title_word_count": len(prediction_request.task_title.split()),
            "description_word_count": len(prediction_request.task_description.split())
            if prediction_request.task_description
            else 0,
            "task_complexity": task_complexity,
        },
        prediction_type=prediction_request.prediction_type,
        predicted_value=predicted_value,
        confidence_score=confidence_score,
        confidence_interval_lower=predicted_value * 0.8,
        confidence_interval_upper=predicted_value * 1.2,
        prediction_context=prediction_request.context,
        model_id=model.id,
        team_id=prediction_request.team_id,
        repository_id=prediction_request.repository_id,
    )

    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    # Add model name to response
    prediction.model_name = model.name

    return prediction


@router.get("/", response_model=List[PredictionResponse])
async def list_predictions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    team_id: Optional[int] = Query(None),
    repository_id: Optional[int] = Query(None),
    status: Optional[PredictionStatus] = Query(None),
    prediction_type: Optional[PredictionType] = Query(None),
    db: Session = Depends(get_db),
):
    """
    List predictions with optional filtering.
    """
    query = db.query(Prediction)

    if team_id:
        query = query.filter(Prediction.team_id == team_id)

    if repository_id:
        query = query.filter(Prediction.repository_id == repository_id)

    if status:
        query = query.filter(Prediction.status == status)

    if prediction_type:
        query = query.filter(Prediction.prediction_type == prediction_type)

    predictions = query.offset(skip).limit(limit).all()

    # Add model names
    for prediction in predictions:
        model = (
            db.query(PredictionModel)
            .filter(PredictionModel.id == prediction.model_id)
            .first()
        )
        prediction.model_name = model.name if model else "Unknown"

    return predictions


@router.get("/{prediction_id}", response_model=PredictionResponse)
async def get_prediction(prediction_id: int, db: Session = Depends(get_db)):
    """
    Get a specific prediction by ID.
    """
    prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")

    # Add model name
    model = (
        db.query(PredictionModel)
        .filter(PredictionModel.id == prediction.model_id)
        .first()
    )
    prediction.model_name = model.name if model else "Unknown"

    return prediction


@router.post("/{prediction_id}/validate")
async def validate_prediction(
    prediction_id: int,
    validation_request: ValidationRequest,
    db: Session = Depends(get_db),
):
    """
    Validate a prediction with actual values.
    """
    prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")

    if prediction.is_validated:
        raise HTTPException(
            status_code=400, detail="Prediction has already been validated"
        )

    # Update prediction with actual values
    prediction.actual_value = validation_request.actual_value
    prediction.validation_date = datetime.utcnow()
    prediction.validation_source = validation_request.validation_source
    prediction.status = PredictionStatus.VALIDATED
    if validation_request.notes:
        prediction.notes = validation_request.notes

    db.commit()

    return {
        "message": "Prediction validated successfully",
        "prediction_id": prediction_id,
        "predicted_value": prediction.predicted_value,
        "actual_value": prediction.actual_value,
        "accuracy_percentage": prediction.accuracy_percentage,
        "absolute_error": prediction.absolute_error,
    }


@router.get("/models/", response_model=List[ModelResponse])
async def list_models(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[ModelStatus] = Query(None),
    prediction_type: Optional[PredictionType] = Query(None),
    db: Session = Depends(get_db),
):
    """
    List prediction models.
    """
    query = db.query(PredictionModel)

    if status:
        query = query.filter(PredictionModel.status == status)

    if prediction_type:
        query = query.filter(PredictionModel.prediction_type == prediction_type)

    models = query.offset(skip).limit(limit).all()
    return models


@router.get("/models/{model_id}", response_model=ModelResponse)
async def get_model(model_id: int, db: Session = Depends(get_db)):
    """
    Get a specific prediction model by ID.
    """
    model = db.query(PredictionModel).filter(PredictionModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    return model


@router.post("/models/{model_id}/deploy")
async def deploy_model(model_id: int, db: Session = Depends(get_db)):
    """
    Deploy a model (set as active).
    """
    model = db.query(PredictionModel).filter(PredictionModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    # Deactivate other models of the same prediction type
    db.query(PredictionModel).filter(
        PredictionModel.prediction_type == model.prediction_type,
        PredictionModel.id != model_id,
    ).update({"status": ModelStatus.DEPRECATED})

    # Activate this model
    model.status = ModelStatus.ACTIVE
    model.deployed_at = datetime.utcnow()

    db.commit()

    return {
        "message": f"Model {model.name} v{model.version} deployed successfully",
        "model_id": model_id,
    }


@router.post("/features/", response_model=dict)
async def create_task_feature(
    feature_request: TaskFeatureRequest, db: Session = Depends(get_db)
):
    """
    Create a task feature record for ML training data.
    """
    # Verify team exists if provided
    if feature_request.team_id:
        team = db.query(Team).filter(Team.id == feature_request.team_id).first()
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

    # Verify repository exists if provided
    if feature_request.repository_id:
        repository = (
            db.query(Repository)
            .filter(Repository.id == feature_request.repository_id)
            .first()
        )
        if not repository:
            raise HTTPException(status_code=404, detail="Repository not found")

    # Extract basic features
    title_words = len(feature_request.task_title.split())
    desc_words = (
        len(feature_request.task_description.split())
        if feature_request.task_description
        else 0
    )

    # Create task feature record
    task_feature = TaskFeature(
        task_source=feature_request.task_source,
        task_source_id=feature_request.task_source_id,
        task_title=feature_request.task_title,
        task_description=feature_request.task_description,
        task_type=feature_request.task_type,
        title_word_count=title_words,
        description_word_count=desc_words,
        team_id=feature_request.team_id,
        repository_id=feature_request.repository_id,
        actual_hours=feature_request.actual_hours,
        actual_story_points=feature_request.actual_story_points,
    )

    db.add(task_feature)
    db.commit()
    db.refresh(task_feature)

    return {
        "message": "Task feature created successfully",
        "feature_id": task_feature.id,
        "has_completion_data": task_feature.has_completion_data,
    }


@router.get("/analytics/accuracy")
async def get_accuracy_analytics(
    team_id: Optional[int] = Query(None),
    prediction_type: Optional[PredictionType] = Query(None),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """
    Get prediction accuracy analytics.
    """
    from datetime import datetime, timedelta

    start_date = datetime.utcnow() - timedelta(days=days)

    # Build query for validated predictions
    query = db.query(Prediction).filter(
        Prediction.status == PredictionStatus.VALIDATED,
        Prediction.validation_date >= start_date,
    )

    if team_id:
        query = query.filter(Prediction.team_id == team_id)

    if prediction_type:
        query = query.filter(Prediction.prediction_type == prediction_type)

    predictions = query.all()

    if not predictions:
        return {
            "message": "No validated predictions found for the specified criteria",
            "total_predictions": 0,
        }

    # Calculate analytics
    accuracies = [p.accuracy_percentage for p in predictions if p.accuracy_percentage]
    errors = [p.absolute_error for p in predictions if p.absolute_error]

    avg_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0
    avg_error = sum(errors) / len(errors) if errors else 0

    # Count predictions within accuracy thresholds
    within_10_percent = len([a for a in accuracies if a >= 90])
    within_25_percent = len([a for a in accuracies if a >= 75])
    within_50_percent = len([a for a in accuracies if a >= 50])

    return {
        "period_days": days,
        "total_predictions": len(predictions),
        "validated_predictions": len(predictions),
        "average_accuracy_percentage": round(avg_accuracy, 2),
        "average_absolute_error": round(avg_error, 2),
        "predictions_within_10_percent": within_10_percent,
        "predictions_within_25_percent": within_25_percent,
        "predictions_within_50_percent": within_50_percent,
        "accuracy_distribution": {
            "within_10_percent_rate": round(
                (within_10_percent / len(predictions)) * 100, 2
            ),
            "within_25_percent_rate": round(
                (within_25_percent / len(predictions)) * 100, 2
            ),
            "within_50_percent_rate": round(
                (within_50_percent / len(predictions)) * 100, 2
            ),
        },
    }


@router.get("/health")
async def predictions_health_check():
    """
    Health check for predictions API.
    """
    return {"status": "healthy", "service": "predictions"}
