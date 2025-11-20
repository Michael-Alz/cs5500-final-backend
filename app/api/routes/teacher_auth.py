from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.db import get_db
from app.models.teacher import Teacher
from app.schemas.teacher_auth import (
    TeacherLoginIn,
    TeacherLoginOut,
    TeacherSignupIn,
    TeacherSignupOut,
)

router = APIRouter()


@router.post("/signup", response_model=TeacherSignupOut)
def signup(user_data: TeacherSignupIn, db: Session = Depends(get_db)) -> TeacherSignupOut:
    """Register a new teacher."""
    # Check if email already exists
    existing_teacher = db.query(Teacher).filter(Teacher.email == user_data.email).first()
    if existing_teacher:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="AUTH_EMAIL_EXISTS")

    # Create new teacher
    hashed_password = hash_password(user_data.password)
    teacher = Teacher(
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name,
    )

    db.add(teacher)
    db.commit()
    db.refresh(teacher)

    return TeacherSignupOut(
        id=str(teacher.id),
        email=str(teacher.email),
        full_name=str(teacher.full_name),
    )


@router.post("/login", response_model=TeacherLoginOut)
def login(user_data: TeacherLoginIn, db: Session = Depends(get_db)) -> TeacherLoginOut:
    """Authenticate a teacher and return JWT token."""
    # Find teacher by email
    teacher = db.query(Teacher).filter(Teacher.email == user_data.email).first()

    if not teacher or not verify_password(user_data.password, str(teacher.password_hash)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="AUTH_INVALID_CREDENTIALS"
        )

    # Create access token
    access_token = create_access_token(str(teacher.id))

    return TeacherLoginOut(
        access_token=access_token,
        token_type="bearer",
        teacher_email=str(teacher.email),
        teacher_full_name=str(teacher.full_name or ""),
    )
