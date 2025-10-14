from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import auth, students

# Create FastAPI app instance
app = FastAPI(
    title="Classroom Engagement API",
    description="Backend for personalized classroom activities",
    version="0.1.0",
)

# ---------------------------------------------------------
# 🌐 CORS (Cross-Origin Resource Sharing)
# ---------------------------------------------------------
# Allow frontend apps (React, Next.js, etc.) to call this API
# You can replace the origins below with your actual frontend URL
origins = [
    "http://localhost:3000",  # local frontend
    "http://127.0.0.1:3000",
    "https://your-frontend-domain.com",  # production frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # allowed domains
    allow_credentials=True,  # allow cookies/auth headers
    allow_methods=["*"],  # allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # allow all headers (e.g. Authorization)
)

# ---------------------------------------------------------
# 🧩 Register routers
# ---------------------------------------------------------
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(students.router, prefix="/students", tags=["Students"])


# ---------------------------------------------------------
# 🩺 Health and root endpoints
# ---------------------------------------------------------
@app.get("/")
def root() -> dict[str, str]:
    """Root endpoint for API verification."""
    return {"message": "Backend is running!"}


@app.get("/health")
async def health_check() -> dict[str, str | int]:
    """Health check endpoint with environment info."""
    return {
        "status": "healthy",
        "app_env": settings.app_env,
        "port": settings.port,
    }
