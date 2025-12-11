"""create initial tables

Revision ID: f0f3503a9851
Revises: 
Create Date: 2025-12-10 14:21:31.780091

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f0f3503a9851'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # create users first
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=True),
        sa.Column('display_name', sa.String(), nullable=True),
        sa.Column('avatar_url', sa.String(), nullable=True),
        sa.Column('provider', sa.String(), nullable=True),
        sa.Column('provider_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('provider_id')
    )
    op.create_index('idx_users_email', 'users', ['email'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # create conversations and messages without inter-table FKs
    op.create_table(
        'conversations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('last_message_id', sa.UUID(), nullable=True),
        sa.Column('last_message_preview', sa.Text(), nullable=True),
        sa.Column('last_message_created_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversations_last_message_id'), 'conversations', ['last_message_id'], unique=False)

    op.create_table(
        'messages',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('conversation_id', sa.UUID(), nullable=False),
        sa.Column('sender_id', sa.UUID(), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('delivered_at', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('seen_at', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('edited_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('deleted_for_everyone', sa.Boolean(), server_default='false', nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_messages_conversation_created_at', 'messages', ['conversation_id', 'created_at'], unique=False)
    op.create_index(op.f('ix_messages_conversation_id'), 'messages', ['conversation_id'], unique=False)

    op.create_table(
        'conversation_participants',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('conversation_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('joined_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('last_read_message_id', sa.UUID(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversation_participants_conversation_id'), 'conversation_participants', ['conversation_id'], unique=False)

    op.create_table(
        'friend_requests',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('from_user_id', sa.UUID(), nullable=False),
        sa.Column('to_user_id', sa.UUID(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('uq_friend_requests_pair', 'friend_requests', ['from_user_id', 'to_user_id'], unique=True)

    op.create_table(
        'friendships',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_a_id', sa.UUID(), nullable=False),
        sa.Column('user_b_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('uq_friendships_pair', 'friendships', ['user_a_id', 'user_b_id'], unique=True)

    op.create_table(
        'message_deletions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('message_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_message_deletions_message_id'), 'message_deletions', ['message_id'], unique=False)
    op.create_index(op.f('ix_message_deletions_user_id'), 'message_deletions', ['user_id'], unique=False)
    op.create_index('uq_message_deletions_pair', 'message_deletions', ['message_id', 'user_id'], unique=True)

    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('token_hash', sa.String(), nullable=False),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('revoked_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token_hash')
    )
    op.create_index('idx_refresh_tokens_user_id', 'refresh_tokens', ['user_id'], unique=False)

    # create foreign keys after tables
    op.create_foreign_key('fk_messages_conversation_id_conversations', 'messages', 'conversations', ['conversation_id'], ['id'])
    op.create_foreign_key('fk_messages_sender_id_users', 'messages', 'users', ['sender_id'], ['id'])
    op.create_foreign_key('fk_conversation_participants_conversation_id_conversations', 'conversation_participants', 'conversations', ['conversation_id'], ['id'])
    op.create_foreign_key('fk_conversation_participants_last_read_message_id_messages', 'conversation_participants', 'messages', ['last_read_message_id'], ['id'])
    op.create_foreign_key('fk_conversation_participants_user_id_users', 'conversation_participants', 'users', ['user_id'], ['id'])
    op.create_foreign_key('fk_friend_requests_from_user_id_users', 'friend_requests', 'users', ['from_user_id'], ['id'])
    op.create_foreign_key('fk_friend_requests_to_user_id_users', 'friend_requests', 'users', ['to_user_id'], ['id'])
    op.create_foreign_key('fk_friendships_user_a_id_users', 'friendships', 'users', ['user_a_id'], ['id'])
    op.create_foreign_key('fk_friendships_user_b_id_users', 'friendships', 'users', ['user_b_id'], ['id'])
    op.create_foreign_key('fk_message_deletions_message_id_messages', 'message_deletions', 'messages', ['message_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_message_deletions_user_id_users', 'message_deletions', 'users', ['user_id'], ['id'])
    op.create_foreign_key('fk_refresh_tokens_user_id_users', 'refresh_tokens', 'users', ['user_id'], ['id'])
    op.create_foreign_key('fk_conversations_last_message_id_messages', 'conversations', 'messages', ['last_message_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    # drop foreign keys / tables in reverse order
    op.drop_constraint('fk_conversations_last_message_id_messages', 'conversations', type_='foreignkey')
    op.drop_constraint('fk_refresh_tokens_user_id_users', 'refresh_tokens', type_='foreignkey')
    op.drop_constraint('fk_message_deletions_user_id_users', 'message_deletions', type_='foreignkey')
    op.drop_constraint('fk_message_deletions_message_id_messages', 'message_deletions', type_='foreignkey')
    op.drop_constraint('fk_friendships_user_b_id_users', 'friendships', type_='foreignkey')
    op.drop_constraint('fk_friendships_user_a_id_users', 'friendships', type_='foreignkey')
    op.drop_constraint('fk_friend_requests_to_user_id_users', 'friend_requests', type_='foreignkey')
    op.drop_constraint('fk_friend_requests_from_user_id_users', 'friend_requests', type_='foreignkey')
    op.drop_constraint('fk_conversation_participants_user_id_users', 'conversation_participants', type_='foreignkey')
    op.drop_constraint('fk_conversation_participants_last_read_message_id_messages', 'conversation_participants', type_='foreignkey')
    op.drop_constraint('fk_conversation_participants_conversation_id_conversations', 'conversation_participants', type_='foreignkey')
    op.drop_constraint('fk_messages_sender_id_users', 'messages', type_='foreignkey')
    op.drop_constraint('fk_messages_conversation_id_conversations', 'messages', type_='foreignkey')

    op.drop_index('idx_refresh_tokens_user_id', table_name='refresh_tokens')
    op.drop_table('refresh_tokens')
    op.drop_index('uq_message_deletions_pair', table_name='message_deletions')
    op.drop_index(op.f('ix_message_deletions_user_id'), table_name='message_deletions')
    op.drop_index(op.f('ix_message_deletions_message_id'), table_name='message_deletions')
    op.drop_table('message_deletions')
    op.drop_index('uq_friendships_pair', table_name='friendships')
    op.drop_table('friendships')
    op.drop_index('uq_friend_requests_pair', table_name='friend_requests')
    op.drop_table('friend_requests')
    
    op.create_foreign_key('fk_conversation_participants_user_id_users', 'conversation_participants', 'users', ['user_id'], ['id'])
    op.create_foreign_key('fk_friend_requests_from_user_id_users', 'friend_requests', 'users', ['from_user_id'], ['id'])
    op.create_foreign_key('fk_friend_requests_to_user_id_users', 'friend_requests', 'users', ['to_user_id'], ['id'])
    op.create_foreign_key('fk_friendships_user_a_id_users', 'friendships', 'users', ['user_a_id'], ['id'])
    op.create_foreign_key('fk_friendships_user_b_id_users', 'friendships', 'users', ['user_b_id'], ['id'])
    op.create_foreign_key('fk_message_deletions_message_id_messages', 'message_deletions', 'messages', ['message_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_message_deletions_user_id_users', 'message_deletions', 'users', ['user_id'], ['id'])
    op.create_foreign_key('fk_refresh_tokens_user_id_users', 'refresh_tokens', 'users', ['user_id'], ['id'])
    op.create_foreign_key('fk_conversations_last_message_id_messages', 'conversations', 'messages', ['last_message_id'], ['id'], ondelete='SET NULL')
    # ### end Alembic commands ###
    sa.PrimaryKeyConstraint('id')
    
    op.create_index(op.f('ix_message_deletions_message_id'), 'message_deletions', ['message_id'], unique=False)
    op.create_index(op.f('ix_message_deletions_user_id'), 'message_deletions', ['user_id'], unique=False)
    op.create_index('uq_message_deletions_pair', 'message_deletions', ['message_id', 'user_id'], unique=True)
    op.create_table('refresh_tokens',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('token_hash', sa.String(), nullable=False),
    sa.Column('expires_at', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.Column('revoked_at', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('token_hash')
    )
    op.create_index('idx_refresh_tokens_user_id', 'refresh_tokens', ['user_id'], unique=False)
    # ### end Alembic commands ###



