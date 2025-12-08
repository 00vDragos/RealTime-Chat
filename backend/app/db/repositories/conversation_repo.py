from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models.conversations import Conversations
from app.models.conversation_participants import ConversationsParticipants
from app.models.users import users


class ConversationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_conversations_for_user(self, user_id: UUID):
        """
        Return all conversations where the user is a participant.
        Ordered by last_message_created_at DESC.
        """
        stmt = (
            select(Conversations)
            .join(ConversationsParticipants)
            .where(ConversationsParticipants.user_id == user_id)
            .order_by(Conversations.last_message_created_at.desc())
        )
        return (await self.db.execute(stmt)).scalars().all()

    async def get_other_participant(self, conversation_id: UUID, user_id: UUID):
        """
        Return the user_id of the other participant in a direct conversation.
        """
        stmt = (
            select(ConversationsParticipants.user_id)
            .where(
                ConversationsParticipants.conversation_id == conversation_id,
                ConversationsParticipants.user_id != user_id
            )
        )
        return (await self.db.execute(stmt)).scalar()

    async def get_user(self, user_id: UUID):
        """
        Load user info (display_name, avatar, etc.)
        """
        stmt = select(users).where(users.id == user_id)
        return (await self.db.execute(stmt)).scalars().first()
