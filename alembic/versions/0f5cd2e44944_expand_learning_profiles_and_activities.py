"""expand learning profiles and activities

Revision ID: 0f5cd2e44944
Revises: 56dc1ae30b44
Create Date: 2025-01-15 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0f5cd2e44944"
down_revision: Union[str, Sequence[str], None] = "56dc1ae30b44"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Apply schema changes for learning profiles and activities."""
    # Courses table updates
    op.add_column(
        "courses",
        sa.Column("baseline_survey_id", sa.String(length=36), nullable=True),
    )
    op.add_column(
        "courses",
        sa.Column(
            "learning_style_categories",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )
    op.add_column(
        "courses",
        sa.Column(
            "mood_labels",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )
    op.add_column(
        "courses",
        sa.Column(
            "requires_rebaseline",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "courses",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
            server_default=sa.text("now()"),
        ),
    )
    op.create_foreign_key(
        "fk_courses_baseline_survey",
        "courses",
        "surveys",
        ["baseline_survey_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Sessions table updates
    op.alter_column(
        "sessions", "survey_template_id", existing_type=sa.String(length=36), nullable=True
    )
    op.add_column(
        "sessions",
        sa.Column(
            "require_survey",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "sessions",
        sa.Column(
            "mood_check_schema",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )
    op.add_column(
        "sessions",
        sa.Column("survey_snapshot_json", sa.JSON(), nullable=True),
    )

    # Submissions table updates
    op.add_column(
        "submissions",
        sa.Column("course_id", sa.String(length=36), nullable=True),
    )
    op.add_column(
        "submissions",
        sa.Column(
            "mood",
            sa.String(length=50),
            nullable=False,
            server_default="unknown",
        ),
    )
    op.add_column(
        "submissions",
        sa.Column(
            "is_baseline_update",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.alter_column("submissions", "answers_json", existing_type=sa.JSON(), nullable=True)
    op.alter_column(
        "submissions",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=sa.text("now()"),
        existing_nullable=True,
    )
    op.create_foreign_key(
        "fk_submissions_course",
        "submissions",
        "courses",
        ["course_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # Populate course_id for existing submissions
    op.execute(
        """
        UPDATE submissions AS sub
        SET course_id = sess.course_id
        FROM sessions AS sess
        WHERE sub.session_id = sess.id
        """
    )
    # Ensure course_id is non-null after backfill
    op.alter_column("submissions", "course_id", existing_type=sa.String(length=36), nullable=False)

    # New tables: activity_types
    op.create_table(
        "activity_types",
        sa.Column("type_name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=1024), nullable=False),
        sa.Column(
            "required_fields", sa.JSON(), nullable=False, server_default=sa.text("'[]'::jsonb")
        ),
        sa.Column(
            "optional_fields", sa.JSON(), nullable=False, server_default=sa.text("'[]'::jsonb")
        ),
        sa.Column("example_content_json", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("type_name"),
    )

    # New table: activities
    op.create_table(
        "activities",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("summary", sa.String(length=1024), nullable=False),
        sa.Column("type", sa.String(length=100), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("content_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("creator_id", sa.String(length=36), nullable=True),
        sa.Column("creator_name", sa.String(length=255), nullable=False),
        sa.Column("creator_email", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["type"], ["activity_types.type_name"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["creator_id"], ["teachers.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    # New table: course_recommendations
    op.create_table(
        "course_recommendations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("course_id", sa.String(length=36), nullable=False),
        sa.Column("learning_style", sa.String(length=100), nullable=True),
        sa.Column("mood", sa.String(length=100), nullable=True),
        sa.Column("activity_id", sa.String(length=36), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["activity_id"], ["activities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "course_id",
            "learning_style",
            "mood",
            name="uq_course_style_mood",
        ),
    )
    op.create_index(
        "ix_course_recommendations_course",
        "course_recommendations",
        ["course_id"],
    )

    # New table: course_student_profiles
    op.create_table(
        "course_student_profiles",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("course_id", sa.String(length=36), nullable=False),
        sa.Column("student_id", sa.String(length=36), nullable=True),
        sa.Column("guest_id", sa.String(length=36), nullable=True),
        sa.Column("latest_submission_id", sa.String(length=36), nullable=True),
        sa.Column("profile_category", sa.String(length=100), nullable=False),
        sa.Column(
            "profile_scores_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")
        ),
        sa.Column(
            "first_captured_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "is_current",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["latest_submission_id"], ["submissions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "course_id",
            "student_id",
            "is_current",
            name="uq_course_student_current",
        ),
        sa.UniqueConstraint(
            "course_id",
            "guest_id",
            "is_current",
            name="uq_course_guest_current",
        ),
    )

    # Cleanup server defaults that should only apply to existing rows
    op.alter_column(
        "courses",
        "learning_style_categories",
        server_default=None,
        existing_type=sa.JSON(),
    )
    op.alter_column(
        "courses",
        "mood_labels",
        server_default=None,
        existing_type=sa.JSON(),
    )
    op.alter_column(
        "courses",
        "requires_rebaseline",
        server_default=None,
        existing_type=sa.Boolean(),
    )
    op.alter_column(
        "courses",
        "updated_at",
        server_default=None,
        existing_type=sa.DateTime(timezone=True),
    )
    op.alter_column(
        "sessions",
        "require_survey",
        server_default=None,
        existing_type=sa.Boolean(),
    )
    op.alter_column(
        "sessions",
        "mood_check_schema",
        server_default=None,
        existing_type=sa.JSON(),
    )
    op.alter_column(
        "submissions",
        "mood",
        server_default=None,
        existing_type=sa.String(length=50),
    )
    op.alter_column(
        "submissions",
        "is_baseline_update",
        server_default=None,
        existing_type=sa.Boolean(),
    )


def downgrade() -> None:
    """Revert schema changes."""
    op.drop_table("course_student_profiles")
    op.drop_index("ix_course_recommendations_course", table_name="course_recommendations")
    op.drop_table("course_recommendations")
    op.drop_table("activities")
    op.drop_table("activity_types")

    op.drop_constraint("fk_submissions_course", "submissions", type_="foreignkey")
    op.alter_column("submissions", "updated_at", server_default=None)
    op.alter_column("submissions", "answers_json", existing_type=sa.JSON(), nullable=False)
    op.drop_column("submissions", "is_baseline_update")
    op.drop_column("submissions", "mood")
    op.drop_column("submissions", "course_id")

    op.drop_column("sessions", "survey_snapshot_json")
    op.drop_column("sessions", "mood_check_schema")
    op.drop_column("sessions", "require_survey")
    op.alter_column(
        "sessions", "survey_template_id", existing_type=sa.String(length=36), nullable=False
    )

    op.drop_constraint("fk_courses_baseline_survey", "courses", type_="foreignkey")
    op.drop_column("courses", "updated_at")
    op.drop_column("courses", "requires_rebaseline")
    op.drop_column("courses", "mood_labels")
    op.drop_column("courses", "learning_style_categories")
    op.drop_column("courses", "baseline_survey_id")
