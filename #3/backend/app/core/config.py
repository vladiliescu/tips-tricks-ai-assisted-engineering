from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    # Application settings
    app_name: str = "GitHub Predictive Analytics"
    debug: bool = False
    version: str = "1.0.0"

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000

    # Database settings
    database_url: str = "sqlite:///./app.db"
    database_echo: bool = False

    # GitHub API settings
    github_token: Optional[str] = None
    github_api_url: str = "https://api.github.com"
    github_webhook_secret: Optional[str] = None

    # Security settings
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS settings
    allowed_origins: list = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # ML Model settings
    model_version: str = "1.0"
    model_retrain_interval_hours: int = 24
    prediction_confidence_threshold: float = 0.7

    # API rate limiting
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60

    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Create settings instance
settings = Settings()

# Create data directory if it doesn't exist
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)
