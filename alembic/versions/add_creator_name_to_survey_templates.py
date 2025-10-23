"""add creator_name to survey_templates

Revision ID: add_creator_name_to_survey_templates
Revises: f69a8eb6dc62
Create Date: 2025-10-22 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_creator_name"
down_revision: Union[str, Sequence[str], None] = "f69a8eb6dc62"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add creator_name column to survey_templates
    op.add_column(
        "survey_templates",
        sa.Column("creator_name", sa.String(length=255), nullable=False, server_default="system"),
    )

    # Remove the server default after adding the column
    op.alter_column("survey_templates", "creator_name", server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    # Remove creator_name column from survey_templates
    op.drop_column("survey_templates", "creator_name")
