"""increase_join_token_length

Revision ID: 4ed757452705
Revises: 0f5cd2e44944
Create Date: 2025-11-01 03:51:59.794106

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4ed757452705"
down_revision: Union[str, Sequence[str], None] = "0f5cd2e44944"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "sessions", "join_token", existing_type=sa.String(length=12), type_=sa.String(length=16)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "sessions", "join_token", existing_type=sa.String(length=16), type_=sa.String(length=12)
    )
