"""initial schema

Revision ID: 6d1b629fcbda
Revises: 
Create Date: 2025-12-08 15:39:04.408988

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "6d1b629fcbda"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---- 1) users (no FK dependencies) ----
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("display_name", sa.String(), nullable=False),
        sa.Column("avatar_url", sa.String(), nullable=True),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("provider_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.String(), nullable=False),
        sa.Column("updated_at", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider_id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    # ---- 2) conversations (WITHOUT FK to messages yet) ----
    op.create_table(
        "conversations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("last_message_id", sa.UUID(), nullable=True),
        sa.Column("last_message_preview", sa.Text(), nullable=True),
        sa.Column("last_message_created_at", sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_conversations_last_message_id"),
        "conversations",
        ["last_message_id"],
        unique=False,
    )

    # ---- 3) messages (depends on conversations + users) ----
    op.create_table(
        "messages",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("conversation_id", sa.UUID(), nullable=False),
        sa.Column("sender_id", sa.UUID(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("delivered_at", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("seen_at", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("edited_at", sa.TIMESTAMP(), nullable=True),
        sa.Column(
            "deleted_for_everyone",
            sa.Boolean(),
            server_default="false",
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"]),
        sa.ForeignKeyConstraint(["sender_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_messages_conversation_created_at",
        "messages",
        ["conversation_id", "created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_messages_conversation_id"),
        "messages",
        ["conversation_id"],
        unique=False,
    )

    # ---- 4) friend_requests (depends on users) ----
    op.create_table(
        "friend_requests",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("from_user_id", sa.UUID(), nullable=False),
        sa.Column("to_user_id", sa.UUID(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(["from_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["to_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "uq_friend_requests_pair",
        "friend_requests",
        ["from_user_id", "to_user_id"],
        unique=True,
    )

    # ---- 5) friendships (depends on users) ----
    op.create_table(
        "friendships",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_a_id", sa.UUID(), nullable=False),
        sa.Column("user_b_id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(["user_a_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["user_b_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "uq_friendships_pair",
        "friendships",
        ["user_a_id", "user_b_id"],
        unique=True,
    )

    # ---- 6) conversation_participants (depends on conversations, messages, users) ----
    op.create_table(
        "conversation_participants",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("conversation_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("joined_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("last_read_message_id", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"]),
        sa.ForeignKeyConstraint(["last_read_message_id"], ["messages.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_conversation_participants_conversation_id"),
        "conversation_participants",
        ["conversation_id"],
        unique=False,
    )

    # ---- 7) message_deletions (depends on messages, users) ----
    op.create_table(
        "message_deletions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("message_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("deleted_at", sa.TIMESTAMP(), nullable=False),
        sa.ForeignKeyConstraint(
            ["message_id"], ["messages.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_message_deletions_message_id"),
        "message_deletions",
        ["message_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_message_deletions_user_id"),
        "message_deletions",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "uq_message_deletions_pair",
        "message_deletions",
        ["message_id", "user_id"],
        unique=True,
    )

    # ---- 8) refresh_tokens (depends on users) ----
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("token_hash", sa.String(), nullable=False),
        sa.Column("expires_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("revoked_at", sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index(
        "idx_refresh_tokens_user_id",
        "refresh_tokens",
        ["user_id"],
        unique=False,
    )

    # ---- 9) add the cyclic FK *after* messages exists ----
    op.create_foreign_key(
        "fk_conversations_last_message_id_messages",
        "conversations",  # source table
        "messages",       # referred table
        ["last_message_id"],
        ["id"],
        ondelete="SET NULL",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # drop the extra FK first to avoid dependency issues
    op.drop_constraint(
        "fk_conversations_last_message_id_messages",
        "conversations",
        type_="foreignkey",
    )

    op.drop_index("idx_refresh_tokens_user_id", table_name="refresh_tokens")
    op.drop_table("refresh_tokens")

    op.drop_index("uq_message_deletions_pair", table_name="message_deletions")
    op.drop_index(
        op.f("ix_message_deletions_user_id"),
        table_name="message_deletions",
    )
    op.drop_index(
        op.f("ix_message_deletions_message_id"),
        table_name="message_deletions",
    )
    op.drop_table("message_deletions")

    op.drop_index("uq_friendships_pair", table_name="friendships")
    op.drop_table("friendships")

    op.drop_index("uq_friend_requests_pair", table_name="friend_requests")
    op.drop_table("friend_requests")

    op.drop_index(
        op.f("ix_conversation_participants_conversation_id"),
        table_name="conversation_participants",
    )
    op.drop_table("conversation_participants")

    op.drop_index(op.f("ix_messages_conversation_id"), table_name="messages")
    op.drop_index("idx_messages_conversation_created_at", table_name="messages")
    op.drop_table("messages")

    op.drop_index(op.f("ix_conversations_last_message_id"), table_name="conversations")
    op.drop_table("conversations")

    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    # ### end Alembic commands ###
