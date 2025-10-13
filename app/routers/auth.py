from fastapi import APIRouter

router = APIRouter()


@router.post("/signup")
def signup_demo() -> dict[str, str]:
    """Demo signup endpoint."""
    return {"message": "user created (demo)"}
