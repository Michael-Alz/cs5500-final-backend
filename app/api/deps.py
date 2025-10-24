from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import verify_token
from app.db import get_db
from app.models.student import Student
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


def get_current_student(
    credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)
) -> Student:
    """Get the current authenticated student."""
    token = credentials.credentials
    student_id = verify_token(token)

    if not student_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Student not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return student


def get_current_student_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db),
) -> Optional[Student]:
    """Get the current authenticated student if token is provided, otherwise return None."""
    if not credentials:
        return None

    try:
        token = credentials.credentials
        student_id = verify_token(token)

        if not student_id:
            return None

        student = db.query(Student).filter(Student.id == student_id).first()
        return student
    except Exception:
        return None
