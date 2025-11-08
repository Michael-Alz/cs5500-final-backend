"""add is_auto flag to course recommendations

Revision ID: 7b3e36c35608
Revises: 0f5cd2e44944
Create Date: 2024-05-16 00:00:00
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "7b3e36c35608"
down_revision = "4ed757452705"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "course_recommendations",
        sa.Column(
            "is_auto",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )


def downgrade() -> None:
    op.drop_column("course_recommendations", "is_auto")
