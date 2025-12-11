"""add last_seen to users

Revision ID: 1f8d88eb47fb
Revises: 6b511658019c
Create Date: 2025-12-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '1f8d88eb47fb'
down_revision: Union[str, Sequence[str], None] = '6b511658019c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column('last_seen', sa.TIMESTAMP(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('users', 'last_seen')
