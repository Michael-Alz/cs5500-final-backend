from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db import get_db
from app.schemas.admin import AdminActionRequest
from app.services.maintenance import clear_database_data
from scripts.seed import seed_data

router = APIRouter()


def _ensure_non_prod_environment() -> None:
    if settings.app_env not in {"dev", "test"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="ADMIN_DISABLED")


def _verify_password(payload: AdminActionRequest) -> None:
    expected = settings.maintenance_admin_password
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ADMIN_PASSWORD_NOT_CONFIGURED",
        )
    if payload.password != expected:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="INVALID_PASSWORD")


@router.post("/reset", status_code=status.HTTP_200_OK)
def reset_database(
    payload: AdminActionRequest, db: Session = Depends(get_db)
) -> dict[str, dict[str, int]]:
    """Delete all data from every table (dev/test only)."""

    _ensure_non_prod_environment()
    _verify_password(payload)

    deleted = clear_database_data(db)
    return {"deleted": deleted}


@router.post("/seed", status_code=status.HTTP_202_ACCEPTED)
def seed_database(payload: AdminActionRequest) -> dict[str, str]:
    """Run the seed script to repopulate demo data (dev/test only)."""

    _ensure_non_prod_environment()
    _verify_password(payload)

    seed_data()
    return {"status": "seeded"}
