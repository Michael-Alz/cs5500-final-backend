"""add_creator_tracking_to_surveys

Revision ID: 3cedd7de2dc4
Revises: cdb7fdd0ba2c
Create Date: 2025-10-23 16:38:49.765673

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3cedd7de2dc4"
down_revision: Union[str, Sequence[str], None] = "cdb7fdd0ba2c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add new columns to surveys table
    op.add_column("surveys", sa.Column("creator_id", sa.String(length=36), nullable=True))
    op.add_column("surveys", sa.Column("creator_email", sa.String(length=255), nullable=True))

    # Add foreign key constraint
    op.create_foreign_key(
        "fk_surveys_creator_id", "surveys", "teachers", ["creator_id"], ["id"], ondelete="CASCADE"
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop foreign key constraint
    op.drop_constraint("fk_surveys_creator_id", "surveys", type_="foreignkey")

    # Drop columns
    op.drop_column("surveys", "creator_email")
    op.drop_column("surveys", "creator_id")
