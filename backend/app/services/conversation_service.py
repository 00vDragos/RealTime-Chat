from uuid import UUID

from app.db.repositories.conversation_repo import ConversationRepository
from app.websocket.manager import manager


class ConversationService:
    def __init__(self, repo: ConversationRepository):
        self.repo = repo

    async def _build_conversation_summary(self, conv, current_user_id: UUID):
        # Determine unread count
        last_read_id = await self.repo.get_last_read_message_id(conv.id, current_user_id)
        unread_count = await self.repo.count_unread_messages(conv.id, current_user_id, last_read_id)

        # Participant IDs and names
        part_ids = await self.repo.get_participant_ids(conv.id)
        participantIds = [str(pid) for pid in part_ids]
        participantNames = []
        for pid in part_ids:
            u = await self.repo.get_user(pid)
            participantNames.append(u.display_name if u and getattr(u, "display_name", None) else "Unknown")

        friendId = None
        friendName = None
        friendAvatar = None
        friendProvider = None
        friendIsOnline = False
        friendLastSeen = None

        if conv.type == "direct":
            other_id = await self.repo.get_other_participant(conv.id, current_user_id)
            if other_id:
                other = await self.repo.get_user(other_id)
                friendId = str(other_id)
                friendName = other.display_name if other and getattr(other, "display_name", None) else "Unknown"
                friendAvatar = other.avatar_url if other and getattr(other, "avatar_url", None) else None
                friendProvider = getattr(other, "provider", None)
                friendIsOnline = manager.is_online(str(other_id))
                friendLastSeen = getattr(other, "last_seen", None)
        else:
            # Group: title or joined names excluding current user
            names_excl_me = [name for pid, name in zip(part_ids, participantNames) if str(pid) != str(current_user_id)]
            friendName = ", ".join(names_excl_me) if names_excl_me else ", ".join(participantNames)

        return {
            "id": str(conv.id),
            "friendId": friendId,
            "friendName": friendName,
            "friendAvatar": friendAvatar,
            "friendProvider": friendProvider,
            "friendIsOnline": friendIsOnline,
            "friendLastSeen": friendLastSeen,
            "lastMessage": conv.last_message_preview,
            "lastMessageTime": conv.last_message_created_at,
            "unreadCount": unread_count,
            "participantIds": participantIds,
            "participantNames": participantNames,
        }

    async def list_conversations(self, current_user_id: UUID):
        conversations = await self.repo.get_conversations_for_user(current_user_id)
        return [await self._build_conversation_summary(conv, current_user_id) for conv in conversations]

    async def create_conversation(self, current_user_id: UUID, participant_ids: list[UUID]):
        participants = list(participant_ids) if participant_ids is not None else []
        if current_user_id not in participants:
            participants.append(current_user_id)

        others = [pid for pid in participants if pid != current_user_id]
        if not others:
            raise ValueError("participant_ids must include at least one other participant")

        conversation_type = "direct" if len(participants) == 2 else "group"

        if conversation_type == "direct":
            other = others[0]
            user_a, user_b = sorted([current_user_id, other], key=lambda x: str(x))
            existing = await self.repo.find_direct_conversation_by_participants(user_a, user_b)
            conversation = existing or await self.repo.create_conversation(conversation_type, participants)
        else:
            existing_group = await self.repo.find_conversation_by_participant_set(participants)
            conversation = existing_group or await self.repo.create_conversation(conversation_type, participants)

        return await self._build_conversation_summary(conversation, current_user_id)

    async def update_group_conversation(self, conversation_id: UUID, current_user_id: UUID, title: str):
        # Update the conversation title and return updated summary
        updated = await self.repo.update_conversation_title(conversation_id, title)
        if not updated:
            # If not found, propagate None or raise
            raise ValueError("Conversation not found")

        return await self._build_conversation_summary(updated, current_user_id)

    async def delete_conversation(self, conversation_id: UUID, current_user_id: UUID):
        # Optionally ensure the user is a participant before delete
        part_ids = await self.repo.get_participant_ids(conversation_id)
        if current_user_id not in part_ids:
            # Not authorized to delete
            raise PermissionError("User is not a participant of the conversation")

        await self.repo.delete_conversation(conversation_id)
