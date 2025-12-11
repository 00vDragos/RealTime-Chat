import uuid
from datetime import datetime
from typing import List, Optional

import httpx
from sqlalchemy import or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.conversations import Conversations
from app.models.friendships import Friendship
from app.models.messages import Message
from app.models.users import User
from app.db.repositories.messages.get_messages import get_messages

OPENAI_PROVIDER = "openai"
OPENAI_BOT_ID = settings.OPENAI_BOT_USER_ID


async def ensure_openai_bot_user(db: AsyncSession) -> User:
    stmt = select(User).where(User.id == OPENAI_BOT_ID)
    result = await db.execute(stmt)
    bot = result.scalars().first()
    if bot:
        # Keep avatar in sync with settings if it's missing
        desired_avatar = settings.OPENAI_BOT_AVATAR_URL
        updated = False
        if desired_avatar and bot.avatar_url != desired_avatar:
            bot.avatar_url = desired_avatar
            updated = True
        if updated:
            await db.commit()
            await db.refresh(bot)
        return bot

    bot = User(
        id=OPENAI_BOT_ID,
        email=settings.OPENAI_BOT_EMAIL,
        display_name=settings.OPENAI_BOT_DISPLAY_NAME,
        avatar_url=settings.OPENAI_BOT_AVATAR_URL,
        provider=OPENAI_PROVIDER,
        provider_sub=settings.OPENAI_BOT_EMAIL,
        hashed_password=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(bot)
    await db.commit()
    await db.refresh(bot)
    return bot


async def ensure_user_has_openai_friendship(db: AsyncSession, user_id: uuid.UUID) -> None:
    if user_id == OPENAI_BOT_ID:
        await ensure_openai_bot_user(db)
        return

    await ensure_openai_bot_user(db)

    stmt = select(Friendship).where(
        or_(
            (Friendship.user_a_id == user_id) & (Friendship.user_b_id == OPENAI_BOT_ID),
            (Friendship.user_a_id == OPENAI_BOT_ID) & (Friendship.user_b_id == user_id),
        )
    )
    res = await db.execute(stmt)
    if res.scalars().first():
        return

    user_a, user_b = (user_id, OPENAI_BOT_ID) if str(user_id) < str(OPENAI_BOT_ID) else (OPENAI_BOT_ID, user_id)
    friendship = Friendship(user_a_id=user_a, user_b_id=user_b)
    db.add(friendship)
    await db.commit()


async def maybe_generate_openai_reply(
    db: AsyncSession,
    conversation_id: uuid.UUID,
    participant_ids: List[uuid.UUID],
    sender_id: uuid.UUID,
) -> Optional[Message]:
    if not settings.OPENAI_API_KEY:
        return None
    if OPENAI_BOT_ID not in participant_ids:
        return None
    if sender_id == OPENAI_BOT_ID:
        return None

    reply = await _call_openai_for_conversation(db, conversation_id)
    if not reply:
        return None

    return await _save_bot_message(db, conversation_id, reply)


async def _call_openai_for_conversation(db: AsyncSession, conversation_id: uuid.UUID) -> Optional[str]:
    history = await get_messages(db, conversation_id, limit=30)
    if len(history) > 25:
        history = history[-25:]

    messages_payload = []
    # We’ll put system prompt into `instructions` instead of as a system message
    instructions = settings.OPENAI_SYSTEM_PROMPT or None

    for msg in history:
        if msg.deleted_for_everyone:
            continue
        if not msg.body:
            continue
        role = "assistant" if msg.sender_id == OPENAI_BOT_ID else "user"
        messages_payload.append(
            {
                "role": role,
                "content": msg.body,
            }
        )

    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.openai.com/v1/responses",
                headers=headers,
                json={
                    "model": settings.OPENAI_MODEL,
                    "input": messages_payload,          # ✅ use `input`
                    "instructions": instructions,       # ✅ system prompt
                    "temperature": 0.7,
                    "max_output_tokens": 512,           # ✅ correct field
                },
            )
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPStatusError as exc:
        # 👇 log the body so you can see exact errors in future
        print(
            "OpenAI request failed",
            exc.response.status_code,
            exc.response.text,
        )
        return None
    except httpx.HTTPError as exc:
        print("OpenAI request failed", exc)
        return None

    outputs = data.get("output") or []
    if not outputs:
        return None

    first_output = outputs[0]
    contents = first_output.get("content") or []
    fragments = [
        item.get("text")
        for item in contents
        if isinstance(item, dict)
        and item.get("type") == "output_text"
        and item.get("text")
    ]
    if not fragments:
        return None

    return "\n".join(fragments)


async def _save_bot_message(db: AsyncSession, conversation_id: uuid.UUID, body: str) -> Message:
    msg = Message(
        id=uuid.uuid4(),
        conversation_id=conversation_id,
        sender_id=OPENAI_BOT_ID,
        body=body.strip(),
        created_at=datetime.utcnow(),
        delivered_at={},
        seen_at={},
        edited_at=None,
        deleted_for_everyone=False,
    )
    db.add(msg)
    await db.flush()

    stmt = (
        update(Conversations)
        .where(Conversations.id == conversation_id)
        .values(
            last_message_id=msg.id,
            last_message_preview=msg.body[:100],
            last_message_created_at=msg.created_at,
        )
    )
    await db.execute(stmt)
    await db.commit()
    await db.refresh(msg)
    return msg
