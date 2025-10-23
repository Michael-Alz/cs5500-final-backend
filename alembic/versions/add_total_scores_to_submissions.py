"""add total_scores to submissions

Revision ID: add_total_scores_to_submissions
Revises: rename_to_surveys
Create Date: 2025-10-22 16:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_total_scores_to_submissions"
down_revision: Union[str, Sequence[str], None] = "rename_to_surveys"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add total_scores column to submissions table
    op.add_column("submissions", sa.Column("total_scores", sa.JSON(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove total_scores column from submissions table
    op.drop_column("submissions", "total_scores")
