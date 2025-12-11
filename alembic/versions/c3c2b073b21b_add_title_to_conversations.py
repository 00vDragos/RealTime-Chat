"""add title to conversations"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c3c2b073b21b"
down_revision = "1f8d88eb47fb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("conversations", sa.Column("title", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("conversations", "title")
