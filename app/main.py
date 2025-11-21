from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    activities,
    activity_types,
    admin,
    courses,
    public,
    sessions,
    student_auth,
    surveys,
    teacher_auth,
)
from app.core.config import settings

# Create FastAPI app instance
app = FastAPI(
    title=settings.app_name,
    description="Backend for QR code-based classroom checkin system",
    version="0.1.0",
)

# ---------------------------------------------------------
# 🌐 CORS (Cross-Origin Resource Sharing)
# ---------------------------------------------------------
# Default: allow all origins. If CORS_ORIGINS is provided, only allow those URLs.
allow_all_origins = not settings.cors_origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[] if allow_all_origins else settings.cors_origins,
    allow_origin_regex=".*" if allow_all_origins else None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# 🧩 Register routers
# ---------------------------------------------------------
app.include_router(teacher_auth.router, prefix="/api/teachers", tags=["Teacher Authentication"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin Tools"])
app.include_router(student_auth.router, prefix="/api/students", tags=["Student Authentication"])
app.include_router(activity_types.router, prefix="/api/activity-types", tags=["Activity Types"])
app.include_router(activities.router, prefix="/api/activities", tags=["Activities"])
app.include_router(courses.router, prefix="/api/courses", tags=["Courses"])
app.include_router(surveys.router, prefix="/api/surveys", tags=["Surveys"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["Sessions"])
app.include_router(public.router, prefix="/api/public", tags=["Public"])


# ---------------------------------------------------------
# 🩺 Health and root endpoints
# ---------------------------------------------------------
@app.get("/")
def root() -> dict[str, str]:
    """Root endpoint for API verification."""
    return {"message": "5500 Backend is running!"}


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint with environment info."""
    return {"status": "ok", "env": settings.app_env}


@app.get("/favicon.ico")
def favicon() -> str:
    """Return empty response for favicon requests."""
    return ""
