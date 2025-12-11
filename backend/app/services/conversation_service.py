from uuid import UUID

from fastapi import HTTPException, status

from app.db.repositories.conversation_repo import ConversationRepository
from app.websocket.manager import manager


class ConversationService:
    def __init__(self, repo: ConversationRepository):
        self.repo = repo

    async def list_conversations(self, current_user_id: UUID):
        conversations = await self.repo.get_conversations_for_user(current_user_id)
        result = []

        for conv in conversations:
            summary = await self._build_conversation_summary(conv, current_user_id)
            if summary:
                result.append(summary)

        return result

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
            if existing:
                conversation = existing
            else:
                conversation = await self.repo.create_conversation(conversation_type, participants)
        else:
            existing_group = await self.repo.find_conversation_by_participant_set(participants)
            if existing_group:
                # If it exists, reuse it instead of raising to keep idempotency
                conversation = existing_group
            else:
                conversation = await self.repo.create_conversation(conversation_type, participants)

        if conversation_type == "direct":
            # Pick the other participant as 'friend' for direct convo summary
            friend_id = others[0]
            friend = await self.repo.get_user(friend_id)
            friend_name = friend.display_name if friend and getattr(friend, "display_name", None) else "Unknown"
            friend_avatar = friend.avatar_url if friend and getattr(friend, "avatar_url", None) else None
            friend_id_out = str(friend_id)
            # Build participant names list for summary
            participant_names = []
            for p in participants:
                u = await self.repo.get_user(p)
                participant_names.append(u.display_name if u and getattr(u, "display_name", None) else "Unknown")
        else:
            # Group conversation summary: build participant names and use them as the group title
            participant_names = []
            for p in participants:
                user = await self.repo.get_user(p)
                participant_names.append(user.display_name if user and getattr(user, "display_name", None) else "Unknown")

            friend_name = ", ".join(participant_names)
            friend_avatar = None
            friend_id_out = None

        summary = {
            "id": str(conversation.id),
            "friendId": friend_id_out,
            "friendName": friend_name,
            "friendAvatar": friend_avatar,
            "friendProvider": friend.provider if friend else None,
            "friendIsOnline": manager.is_online(str(friend_id)),
            "friendLastSeen": friend.last_seen if friend else None,
            "lastMessage": preview,
            "lastMessageTime": conv.last_message_created_at,
            "unreadCount": unread_count,
            "participantIds": [str(friend_id), str(current_user_id)],
            "participantNames": [friend_name, current_name],
        }
