from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import Optional
from sqlalchemy.orm import attributes

from app.models.messages import Message

async def change_reaction(
    db: AsyncSession,
    message_id: UUID,
    user_id: UUID,
    new_reaction_type: str
) -> Message:
    """change a user's reaction from one emoji to another """
    stmt = select(Message).where(Message.id == message_id)
    result = await db.execute(stmt)
    message = result.scalar_one_or_none()
    
    if not message:
        raise ValueError("Message not found")
    
    reactions = message.reactions or {}
    user_id_str = str(user_id)
    
    current_reaction = None
    for emoji, user_ids in reactions.items():
        if user_id_str in user_ids:
            current_reaction = emoji
            break
    
    if not current_reaction:
        raise ValueError(
            "User has no current reaction on this message")
    
    if current_reaction == new_reaction_type:
        return message
    
    reactions[current_reaction].remove(user_id_str)
    if not reactions[current_reaction]:
        del reactions[current_reaction]
    
    if new_reaction_type not in reactions:
        reactions[new_reaction_type] = []
    
    reactions[new_reaction_type].append(user_id_str)
     
    message.reactions = reactions
    attributes.flag_modified(message, "reactions")
    
    await db.commit()
    await db.refresh(message)
    
    return message