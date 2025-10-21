import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="Predictive Analytics API",
    description="API for GitHub-based effort estimation",
    version="1.0.0",
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:4173",
    ],  # SvelteKit dev and preview ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Basic health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "predictive-analytics-api"}


# Placeholder API routes
@app.get("/api/repositories")
async def get_repositories():
    return {"repositories": []}


@app.get("/api/teams")
async def get_teams():
    return {"teams": []}


@app.post("/api/predictions")
async def create_prediction():
    return {"prediction": {"effort": 0, "confidence": 0.0}}


# Serve static files (built frontend)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


# Serve frontend for all other routes
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    # Check if static directory exists and serve index.html
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    return {"message": "Frontend not built yet"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
