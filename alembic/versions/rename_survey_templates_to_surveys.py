"""rename survey_templates to surveys

Revision ID: rename_survey_templates_to_surveys
Revises: add_creator_name
Create Date: 2025-10-22 16:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "rename_to_surveys"
down_revision: Union[str, Sequence[str], None] = "add_creator_name"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Check if survey_templates table exists before renaming
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()

    if "survey_templates" in tables and "surveys" not in tables:
        # Rename the table from survey_templates to surveys
        op.rename_table("survey_templates", "surveys")

        # Rename the index
        op.execute("ALTER INDEX ix_survey_template_title RENAME TO ix_surveys_title")
    elif "surveys" in tables:
        # Table already exists, just rename the index if it exists
        try:
            op.execute("ALTER INDEX ix_survey_template_title RENAME TO ix_surveys_title")
        except Exception:
            pass  # Index might not exist or already renamed


def downgrade() -> None:
    """Downgrade schema."""
    # Rename the table back from surveys to survey_templates
    op.rename_table("surveys", "survey_templates")

    # Rename the index back
    op.execute("ALTER INDEX ix_surveys_title RENAME TO ix_survey_template_title")
