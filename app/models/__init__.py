# Import Base from app.db to avoid circular imports
from app.db import Base  # noqa: F401

from .class_session import ClassSession  # noqa: F401
from .course import Course  # noqa: F401
from .student import Student  # noqa: F401
from .submission import Submission  # noqa: F401
from .survey_template import SurveyTemplate  # noqa: F401

# Import all models here so that Base.metadata contains every table
# This ensures Alembic can detect all schema changes automatically.
from .teacher import Teacher  # noqa: F401
