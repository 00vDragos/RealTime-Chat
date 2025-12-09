from uuid import UUID
from app.db.repositories.conversation_repo import ConversationRepository


class ConversationService:
    def __init__(self, repo: ConversationRepository):
        self.repo = repo

    async def list_conversations(self, current_user_id: UUID):
        conversations = await self.repo.get_conversations_for_user(current_user_id)
        result = []

        for conv in conversations:
            friend_id = await self.repo.get_other_participant(conv.id, current_user_id)
            if not friend_id:
                # group conversation or inconsistent data
                continue

            friend = await self.repo.get_user(friend_id)

            preview = conv.last_message_preview or ""
            if preview.strip().lower() == "__deleted__":
                preview = "(deleted message)"

            result.append({
                "id": str(conv.id),
                "friendId": str(friend_id),
                "friendName": friend.display_name if friend else "Unknown",
                "lastMessage": preview,
                "lastMessageTime": conv.last_message_created_at,
                "unreadCount": 0
            })

        return result
