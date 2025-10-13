from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_students_demo() -> list[dict[str, str]]:
    """Demo: return a few student examples."""
    return [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}]
