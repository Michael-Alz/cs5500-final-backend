from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.db import get_db
from app.models.teacher import Teacher
from app.schemas.auth import AuthLoginIn, AuthLoginOut, AuthSignupIn, AuthSignupOut

router = APIRouter()


@router.post("/signup", response_model=AuthSignupOut)
def signup(user_data: AuthSignupIn, db: Session = Depends(get_db)) -> AuthSignupOut:
    """Register a new teacher."""
    # Check if email already exists
    existing_teacher = db.query(Teacher).filter(Teacher.email == user_data.email).first()
    if existing_teacher:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="AUTH_EMAIL_EXISTS")

    # Create new teacher
    hashed_password = hash_password(user_data.password)
    teacher = Teacher(email=user_data.email, password_hash=hashed_password)

    db.add(teacher)
    db.commit()
    db.refresh(teacher)

    return AuthSignupOut(id=str(teacher.id), email=str(teacher.email))


@router.post("/login", response_model=AuthLoginOut)
def login(user_data: AuthLoginIn, db: Session = Depends(get_db)) -> AuthLoginOut:
    """Authenticate a teacher and return JWT token."""
    # Find teacher by email
    teacher = db.query(Teacher).filter(Teacher.email == user_data.email).first()

    if not teacher or not verify_password(user_data.password, str(teacher.password_hash)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="AUTH_INVALID_CREDENTIALS"
        )

    # Create access token
    access_token = create_access_token(str(teacher.id))

    return AuthLoginOut(access_token=access_token, token_type="bearer")
