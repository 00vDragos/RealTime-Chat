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
                # group conversation: include participant ids so frontend can detect duplicates
                participant_ids = await self.repo.get_participant_ids(conv.id)
                preview = conv.last_message_preview or ""
                if preview.strip().lower() == "__deleted__":
                    preview = "(deleted message)"

                # Unread count: messages after last_read, sent by others
                last_read_id = await self.repo.get_last_read_message_id(conv.id, current_user_id)
                unread_count = await self.repo.count_unread_messages(conv.id, current_user_id, last_read_id)

                result.append({
                    "id": str(conv.id),
                    "friendId": None,
                    "friendName": f"Group ({len(participant_ids)} members)",
                    "lastMessage": preview,
                    "lastMessageTime": conv.last_message_created_at,
                    "unreadCount": unread_count,
                    "participantIds": [str(p) for p in participant_ids],
                    "participantNames": [
                        (await self.repo.get_user(p)).display_name if await self.repo.get_user(p) else "Unknown"
                        for p in participant_ids
                    ],
                })
                continue

            friend = await self.repo.get_user(friend_id)
            friend_avatar = None
            if friend and getattr(friend, "avatar_url", None):
                friend_avatar = friend.avatar_url

            preview = conv.last_message_preview or ""
            if preview.strip().lower() == "__deleted__":
                preview = "(deleted message)"

            # Unread count: messages after last_read, sent by others
            last_read_id = await self.repo.get_last_read_message_id(conv.id, current_user_id)
            unread_count = await self.repo.count_unread_messages(conv.id, current_user_id, last_read_id)

            result.append({
                "id": str(conv.id),
                "friendId": str(friend_id),
                "friendName": friend.display_name if friend else "Unknown",
                "friendAvatar": friend_avatar,
                "lastMessage": preview,
                "lastMessageTime": conv.last_message_created_at,
                "unreadCount": unread_count,
                "participantIds": [str(friend_id), str(current_user_id)],
                "participantNames": [
                    friend.display_name if friend and getattr(friend, "display_name", None) else "Unknown",
                    (await self.repo.get_user(current_user_id)).display_name if await self.repo.get_user(current_user_id) else "You"
                ]
            })

        return result

    async def create_conversation(self, current_user_id: UUID, participant_ids: list[UUID]):
        
        participants = list(participant_ids) if participant_ids is not None else []
        if current_user_id not in participants:
            participants.append(current_user_id)

        # Validate there is at least one other participant
        others = [pid for pid in participants if pid != current_user_id]
        if not others:
            raise ValueError("participant_ids must include at least one other participant")

        # Determine conversation type: direct for exactly 2 participants, otherwise group
        conversation_type = "direct" if len(participants) == 2 else "group"

        # For direct conversations, check for existing between the two participants
        if conversation_type == "direct":
            # Direct must be exactly two participants: current user + one other
            other = others[0]
            user_a, user_b = sorted([current_user_id, other], key=lambda x: str(x))
            existing = await self.repo.find_direct_conversation_by_participants(user_a, user_b)
            if existing:
                conversation = existing
            else:
                conversation = await self.repo.create_conversation(conversation_type, participants)
        else:
            # For groups, check if a conversation with the exact participant set already exists
            existing_group = await self.repo.find_conversation_by_participant_set(participants)
            if existing_group:
                # Prevent creating duplicate group conversations
                raise ValueError("A conversation with the same participants already exists")
            conversation = await self.repo.create_conversation(conversation_type, participants)

        if conversation_type == "direct":
            # Pick the other participant as 'friend' for direct convo summary
            friend_id = others[0]
            friend = await self.repo.get_user(friend_id)
            friend_name = friend.display_name if friend and getattr(friend, "display_name", None) else "Unknown"
            friend_avatar = friend.avatar_url if friend and getattr(friend, "avatar_url", None) else None
            friend_id_out = str(friend_id)
        else:
            # Group conversation summary
            friend_name = f"Group ({len(participants)} members)"
            friend_avatar = None
            friend_id_out = None

        summary = {
            "id": str(conversation.id),
            "friendId": friend_id_out,
            "friendName": friend_name,
            "friendAvatar": friend_avatar,
            "lastMessage": None,
            "lastMessageTime": None,
            "unreadCount": 0,
            "participantIds": [str(p) for p in participants]
        }
        return summary