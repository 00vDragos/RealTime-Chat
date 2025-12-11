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
                raise ValueError("A conversation with the same participants already exists")
            default_title = f"Group ({len(participants)} members)"
            conversation = await self.repo.create_conversation(conversation_type, participants, title=default_title)

        return await self._build_conversation_summary(conversation, current_user_id)

    async def update_group_conversation(self, conversation_id: UUID, current_user_id: UUID, title: str):
        conversation = await self.repo.get_conversation_by_id(conversation_id)
        if not conversation:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Conversation not found")

        participant_ids = await self.repo.get_participant_ids(conversation_id)
        if current_user_id not in participant_ids:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "You are not part of this conversation")

        if conversation.type != "group":
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Only group conversations can be edited")

        cleaned_title = title.strip()
        if not cleaned_title:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Title cannot be empty")

        updated = await self.repo.update_conversation_title(conversation_id, cleaned_title)
        if not updated:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Conversation not found")

        return await self._build_conversation_summary(updated, current_user_id)

    async def delete_conversation(self, conversation_id: UUID, current_user_id: UUID):
        conversation = await self.repo.get_conversation_by_id(conversation_id)
        if not conversation:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Conversation not found")

        participant_ids = await self.repo.get_participant_ids(conversation_id)
        if current_user_id not in participant_ids:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "You are not part of this conversation")

        await self.repo.delete_conversation(conversation_id)

    async def _build_conversation_summary(self, conv, current_user_id: UUID):
        preview = conv.last_message_preview or ""
        if preview.strip().lower() == "__deleted__":
            preview = "(deleted message)"

        last_read_id = await self.repo.get_last_read_message_id(conv.id, current_user_id)
        unread_count = await self.repo.count_unread_messages(conv.id, current_user_id, last_read_id)

        if conv.type == "group":
            participant_ids = await self.repo.get_participant_ids(conv.id)
            participant_names: list[str] = []
            for pid in participant_ids:
                user = await self.repo.get_user(pid)
                participant_names.append(
                    user.display_name if user and getattr(user, "display_name", None) else "Unknown"
                )

            title_clean = (conv.title or "").strip()

            if title_clean:
                display_name = title_clean
            else:
                # No explicit title set yet: build a name from participants.
                # Exclude the current user where possible and truncate long lists.
                zipped = list(zip(participant_ids, participant_names))

                if len(zipped) > 0:
                    # Exclude current user if present
                    others = [item for item in zipped if str(item[0]) != str(current_user_id)]

                    # If exclusion produced too few names, fall back to full list
                    if len(others) < 2 and len(zipped) >= 2:
                        others = zipped

                    if len(others) == 0:
                        display_name = f"Group ({len(participant_ids)} members)"
                    elif len(others) <= 3:
                        display_name = ", ".join(name for _, name in others)
                    else:
                        visible = ", ".join(name for _, name in others[:3])
                        display_name = f"{visible}, +{len(others) - 3}"
                else:
                    display_name = f"Group ({len(participant_ids)} members)"

            return {
                "id": str(conv.id),
                "friendId": None,
                "friendName": display_name,
                "friendAvatar": None,
                "friendProvider": None,
                "friendIsOnline": False,
                "friendLastSeen": None,
                "lastMessage": preview,
                "lastMessageTime": conv.last_message_created_at,
                "unreadCount": unread_count,
                "participantIds": [str(p) for p in participant_ids],
                "participantNames": participant_names,
            }

        friend_id = await self.repo.get_other_participant(conv.id, current_user_id)
        if not friend_id:
            return None

        friend = await self.repo.get_user(friend_id)
        friend_avatar = friend.avatar_url if friend and getattr(friend, "avatar_url", None) else None
        friend_name = friend.display_name if friend and getattr(friend, "display_name", None) else "Unknown"

        current_user = await self.repo.get_user(current_user_id)
        current_name = (
            current_user.display_name if current_user and getattr(current_user, "display_name", None) else "You"
        )

        return {
            "id": str(conv.id),
            "friendId": str(friend_id),
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
