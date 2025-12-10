from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models.conversations import Conversations
from app.models.conversation_participants import ConversationsParticipants
from app.models.users import User
from app.models.messages import Message
from sqlalchemy import func


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

    async def get_last_read_message_id(self, conversation_id: UUID, user_id: UUID):
        stmt = (
            select(ConversationsParticipants.last_read_message_id)
            .where(
                ConversationsParticipants.conversation_id == conversation_id,
                ConversationsParticipants.user_id == user_id,
            )
        )
        return (await self.db.execute(stmt)).scalar()

    async def count_unread_messages(self, conversation_id: UUID, user_id: UUID, last_read_message_id: UUID | None):
        # Count messages after last_read that were sent by others and not deleted
        # If last_read_message_id is None, count all messages from others
        base = select(func.count()).select_from(Message).where(
            Message.conversation_id == conversation_id,
            Message.sender_id != user_id,
            Message.deleted_for_everyone == False,  # noqa: E712
        )
        if last_read_message_id:
            # Get timestamp of last read message and count those created after
            ts_stmt = select(Message.created_at).where(Message.id == last_read_message_id)
            ts = (await self.db.execute(ts_stmt)).scalar()
            if ts:
                base = base.where(Message.created_at > ts)
        return (await self.db.execute(base)).scalar() or 0

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
        stmt = select(User).where(User.id == user_id)
        return (await self.db.execute(stmt)).scalars().first()

    async def create_conversation(self, conversation_type: str, participant_ids: list[UUID]):
        """
        Create a new conversation with the given participants.
        """
        new_conversation = Conversations(type=conversation_type)
        self.db.add(new_conversation)
        await self.db.flush()  # to get the new conversation ID

        for pid in participant_ids:
            participant = ConversationsParticipants(
                conversation_id=new_conversation.id,
                user_id=pid
            )
            self.db.add(participant)

        await self.db.commit()
        return new_conversation

    async def find_direct_conversation_by_participants(self, user_a: UUID, user_b: UUID):
        """
        Return an existing direct conversation that includes exactly the two participants provided,
        or None if not found.
        """
        # Find conversations where type is direct and that have both participants
        stmt = (
            select(Conversations)
            .where(Conversations.type == "direct")
        )
        conversations = (await self.db.execute(stmt)).scalars().all()

        # Filter in python: ensure the participants set matches exactly {user_a, user_b}
        for conv in conversations:
            parts_stmt = select(ConversationsParticipants.user_id).where(ConversationsParticipants.conversation_id == conv.id)
            part_ids = set((await self.db.execute(parts_stmt)).scalars().all())
            if part_ids == {user_a, user_b}:
                return conv
        return None