"""add hashed_password and adjust user constraints

Revision ID: 90814b5b15e1
Revises: eb6a66bd3f23
Create Date: 2025-12-08 16:40:39.989100

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '90814b5b15e1'
down_revision: Union[str, None] = 'eb6a66bd3f23'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('hashed_password', sa.String(), nullable=True))
    op.alter_column('users', 'provider_sub',
                    existing_type=sa.String(),
                    nullable=True)
def downgrade() -> None:
    op.alter_column('users', 'provider_sub',
                    existing_type=sa.String(),
                    nullable=False)
    op.drop_column('users', 'hashed_password')
