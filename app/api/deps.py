from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import verify_token
from app.db import get_db
from app.models.teacher import Teacher

security = HTTPBearer()


def get_current_teacher(
    credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)
) -> Teacher:
    """Get the current authenticated teacher."""
    token = credentials.credentials
    teacher_id = verify_token(token)

    if not teacher_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Teacher not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return teacher
