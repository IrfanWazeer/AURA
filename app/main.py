from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.tasks import router as tasks_router
from app.api.goals import router as goals_router
from app.api.habits import router as habits_router
app = FastAPI(
    title="AURA - AI Personal Life Operating System",
    description="Backend API framework handling async agentic routines.",
    version="0.1.0"
)
# Configure CORS cross-origin allowances for front-end integration apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Include the Authentication Router under v1 API version prefix grouping
app.include_router(auth_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")
app.include_router(goals_router, prefix="/api/v1")
app.include_router(habits_router, prefix="/api/v1")

@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "online",
        "system": "AURA OS",
        "message": "Welcome to your AI Personal Life Operating System."
    }