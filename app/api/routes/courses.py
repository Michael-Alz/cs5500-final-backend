from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_teacher
from app.db import get_db
from app.models.course import Course
from app.models.teacher import Teacher
from app.schemas.course import CourseCreate, CourseOut

router = APIRouter()


@router.post("/", response_model=CourseOut)
def create_course(
    course_data: CourseCreate,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher),
) -> CourseOut:
    """Create a new course."""
    try:
        course = Course(title=course_data.title, teacher_id=current_teacher.id)

        db.add(course)
        db.commit()
        db.refresh(course)

        return CourseOut(id=str(course.id), title=str(course.title))

    except IntegrityError as e:
        db.rollback()
        # Check if it's a unique constraint violation
        if "uq_course_title_per_teacher" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A course with this title already exists for your account",
            )
        else:
            # Re-raise other integrity errors
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error occurred"
            )


@router.get("/", response_model=List[CourseOut])
def list_courses(
    db: Session = Depends(get_db), current_teacher: Teacher = Depends(get_current_teacher)
) -> List[CourseOut]:
    """List all courses for the authenticated teacher."""
    courses = db.query(Course).filter(Course.teacher_id == current_teacher.id).all()
    return [CourseOut(id=str(course.id), title=str(course.title)) for course in courses]
