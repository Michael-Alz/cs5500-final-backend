"""fix_guest_name_nullable

Revision ID: cdb7fdd0ba2c
Revises: 80f87c814130
Create Date: 2025-10-23 15:26:10.501094

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "cdb7fdd0ba2c"
down_revision: Union[str, Sequence[str], None] = "80f87c814130"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Make guest_name nullable to allow student submissions
    op.alter_column("submissions", "guest_name", nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    # Make guest_name NOT NULL again (but this will break student submissions)
    op.alter_column("submissions", "guest_name", nullable=False)
