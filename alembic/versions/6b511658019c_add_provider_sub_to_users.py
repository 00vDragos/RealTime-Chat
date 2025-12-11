"""add provider_sub to users

Revision ID: 6b511658019c
Revises: 827a801e11dc
Create Date: 2025-12-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '6b511658019c'
down_revision: Union[str, Sequence[str], None] = '827a801e11dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column('provider_sub', sa.String(length=255), nullable=True, unique=True),
    )


def downgrade() -> None:
    op.drop_column('users', 'provider_sub')
