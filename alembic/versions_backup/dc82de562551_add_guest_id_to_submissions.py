"""add_guest_id_to_submissions

Revision ID: dc82de562551
Revises: 3cedd7de2dc4
Create Date: 2025-10-23 17:09:06.139110

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "dc82de562551"
down_revision: Union[str, Sequence[str], None] = "3cedd7de2dc4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add guest_id column to submissions table
    op.add_column("submissions", sa.Column("guest_id", sa.String(length=36), nullable=True))

    # Generate guest_id for existing guest submissions
    op.execute(
        """
        UPDATE submissions 
        SET guest_id = gen_random_uuid()::text 
        WHERE guest_name IS NOT NULL AND guest_id IS NULL
    """
    )

    # Drop old unique constraint
    op.drop_constraint("uq_session_guest", "submissions", type_="unique")

    # Create new unique constraint using guest_id instead of guest_name
    op.create_unique_constraint("uq_session_guest_id", "submissions", ["session_id", "guest_id"])

    # Update check constraint to include guest_id
    op.drop_constraint("ck_submission_student_or_guest", "submissions", type_="check")
    op.create_check_constraint(
        "ck_submission_student_or_guest",
        "submissions",
        "(student_id IS NOT NULL AND guest_name IS NULL AND guest_id IS NULL) OR "
        "(student_id IS NULL AND guest_name IS NOT NULL AND guest_id IS NOT NULL)",
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop new unique constraint
    op.drop_constraint("uq_session_guest_id", "submissions", type_="unique")

    # Recreate old unique constraint
    op.create_unique_constraint("uq_session_guest", "submissions", ["session_id", "guest_name"])

    # Revert check constraint
    op.drop_constraint("ck_submission_student_or_guest", "submissions", type_="check")
    op.create_check_constraint(
        "ck_submission_student_or_guest",
        "submissions",
        "(student_id IS NOT NULL AND guest_name IS NULL) OR "
        "(student_id IS NULL AND guest_name IS NOT NULL)",
    )

    # Drop guest_id column
    op.drop_column("submissions", "guest_id")
