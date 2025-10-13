from fastapi import FastAPI

from app.core.config import settings
from app.routers import auth, students

app = FastAPI(
    title="Classroom Engagement API",
    description="Backend for personalized classroom activities",
    version="0.1.0",
)

# Register routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(students.router, prefix="/students", tags=["Students"])


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Backend is running!"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "env": settings.app_env}
