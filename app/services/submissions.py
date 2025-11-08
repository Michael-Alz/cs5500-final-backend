from __future__ import annotations

from typing import Dict, Optional

from sqlalchemy.orm import Session

from app.models.class_session import ClassSession
from app.models.course import Course
from app.models.course_student_profile import CourseStudentProfile
from app.models.student import Student
from app.models.submission import Submission


def get_current_profile(
    db: Session,
    course_id: str,
    student_id: Optional[str] = None,
    guest_id: Optional[str] = None,
) -> Optional[CourseStudentProfile]:
    """Return the current profile for a participant within a course."""
    query = db.query(CourseStudentProfile).filter(
        CourseStudentProfile.course_id == course_id,
        CourseStudentProfile.is_current.is_(True),
    )
    if student_id:
        query = query.filter(CourseStudentProfile.student_id == student_id)
    else:
        query = query.filter(CourseStudentProfile.guest_id == guest_id)

    return query.first()


def upsert_submission(
    db: Session,
    session: ClassSession,
    course: Course,
    mood: str,
    answers: Optional[Dict[str, str]],
    total_scores: Optional[Dict[str, int]],
    is_baseline_update: bool,
    student: Optional[Student] = None,
    guest_id: Optional[str] = None,
    guest_name: Optional[str] = None,
) -> Submission:
    """Create or update a submission for the participant."""
    submission_query = db.query(Submission).filter(Submission.session_id == session.id)
    if student:
        submission_query = submission_query.filter(Submission.student_id == student.id)
    else:
        submission_query = submission_query.filter(Submission.guest_id == guest_id)

    submission = submission_query.first()
    status = "completed" if answers else "completed"  # Mood check counts as completion

    if submission:
        submission.course_id = course.id
        submission.mood = mood
        submission.answers_json = answers
        submission.total_scores = total_scores
        submission.is_baseline_update = is_baseline_update
        submission.status = status
    else:
        submission = Submission(
            session_id=session.id,
            course_id=course.id,
            student_id=student.id if student else None,
            guest_id=guest_id if not student else None,
            guest_name=guest_name if not student else None,
            mood=mood,
            answers_json=answers,
            total_scores=total_scores,
            is_baseline_update=is_baseline_update,
            status=status,
        )
        db.add(submission)

    return submission


def update_course_student_profile(
    db: Session,
    course: Course,
    submission: Submission,
    learning_style: str,
    total_scores: Dict[str, int],
    student: Optional[Student] = None,
    guest_id: Optional[str] = None,
) -> CourseStudentProfile:
    """Mark previous profiles as stale and insert a new current profile."""
    query = db.query(CourseStudentProfile).filter(
        CourseStudentProfile.course_id == course.id,
    )
    if student:
        query = query.filter(CourseStudentProfile.student_id == student.id)
    else:
        query = query.filter(CourseStudentProfile.guest_id == guest_id)

    query.update({"is_current": False}, synchronize_session=False)

    profile = CourseStudentProfile(
        course_id=course.id,
        student_id=student.id if student else None,
        guest_id=guest_id if not student else None,
        latest_submission_id=submission.id,
        profile_category=learning_style,
        profile_scores_json=total_scores,
        is_current=True,
    )
    db.add(profile)
    return profile
