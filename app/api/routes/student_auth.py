from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_student
from app.core.security import create_access_token, hash_password, verify_password
from app.db import get_db
from app.models.student import Student
from app.schemas.student_auth import (
    StudentLoginIn,
    StudentLoginOut,
    StudentProfileOut,
    StudentSignupIn,
    StudentSignupOut,
    StudentSubmissionHistoryItem,
    StudentSubmissionHistoryOut,
)
from app.services.submissions import split_answers_payload

router = APIRouter()


@router.post("/signup", response_model=StudentSignupOut)
def signup(student_data: StudentSignupIn, db: Session = Depends(get_db)) -> StudentSignupOut:
    """Register a new student."""
    # Check if email already exists
    existing_student = db.query(Student).filter(Student.email == student_data.email).first()
    if existing_student:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="AUTH_EMAIL_EXISTS")

    # Create new student
    hashed_password = hash_password(student_data.password)
    student = Student(
        email=student_data.email,
        password_hash=hashed_password,
        full_name=student_data.full_name,
    )

    db.add(student)
    db.commit()
    db.refresh(student)

    return StudentSignupOut(
        id=str(student.id),
        email=str(student.email),
        full_name=str(student.full_name),
    )


@router.post("/login", response_model=StudentLoginOut)
def login(student_data: StudentLoginIn, db: Session = Depends(get_db)) -> StudentLoginOut:
    """Authenticate a student and return JWT token."""
    # Find student by email
    student = db.query(Student).filter(Student.email == student_data.email).first()

    if not student or not verify_password(student_data.password, str(student.password_hash)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="AUTH_INVALID_CREDENTIALS"
        )

    # Create access token
    access_token = create_access_token(str(student.id))

    return StudentLoginOut(
        access_token=access_token,
        token_type="bearer",
        student_email=str(student.email),
        student_full_name=str(student.full_name),
    )


@router.get("/me", response_model=StudentProfileOut)
def get_current_student_profile(
    current_student: Student = Depends(get_current_student),
) -> StudentProfileOut:
    """Get current student profile."""
    return StudentProfileOut(
        id=str(current_student.id),
        email=str(current_student.email),
        full_name=str(current_student.full_name),
        created_at=current_student.created_at,  # type: ignore[arg-type]
    )


@router.get("/submissions", response_model=StudentSubmissionHistoryOut)
def get_student_submissions(
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
) -> StudentSubmissionHistoryOut:
    """Get student's submission history."""
    from app.models.class_session import ClassSession
    from app.models.course import Course
    from app.models.submission import Submission

    # Get all submissions for this student
    submissions = (
        db.query(Submission)
        .filter(Submission.student_id == current_student.id)
        .join(ClassSession, Submission.session_id == ClassSession.id)
        .join(Course, ClassSession.course_id == Course.id)
        .order_by(Submission.created_at.desc())
        .all()
    )

    items = []
    for submission in submissions:
        # Get course title
        session = db.query(ClassSession).filter(ClassSession.id == submission.session_id).first()
        course_title = "Unknown Course"
        if session and session.course:
            course_title = session.course.title

        raw_answers, answer_details = split_answers_payload(submission.answers_json)

        items.append(
            StudentSubmissionHistoryItem(
                id=str(submission.id),
                session_id=str(submission.session_id),
                course_title=course_title,
                answers=dict(raw_answers) if raw_answers else {},
                answer_details=dict(answer_details) if answer_details else None,
                total_scores=dict(submission.total_scores) if submission.total_scores else None,
                status=str(submission.status),
                created_at=submission.created_at,  # type: ignore[arg-type]
                updated_at=submission.updated_at,  # type: ignore[arg-type]
            )
        )

    return StudentSubmissionHistoryOut(submissions=items, total=len(items))
