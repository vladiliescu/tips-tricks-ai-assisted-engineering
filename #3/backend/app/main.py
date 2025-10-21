from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager

from app.api import github, teams, predictions, analytics
from app.core.config import settings
from app.core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")
    await init_db()
    yield
    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title="GitHub Predictive Analytics API",
    description="API for predicting development effort based on GitHub data and team parameters",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/")
async def root():
    return {"message": "GitHub Predictive Analytics API", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}


# Include API routers
app.include_router(github.router, prefix="/api/v1/github", tags=["GitHub"])
app.include_router(teams.router, prefix="/api/v1/teams", tags=["Teams"])
app.include_router(
    predictions.router, prefix="/api/v1/predictions", tags=["Predictions"]
)
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred", "detail": str(exc)},
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
