from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from sqlalchemy.orm import attributes

from app.models.messages import Message

async def remove_reaction(
    db: AsyncSession,
    message_id: UUID,
    user_id: UUID,
    reaction_type: str
) -> Message:
    """remove reaction from a message"""
    stmt = select(Message).where(Message.id == message_id)
    result = await db.execute(stmt)
    message = result.scalar_one_or_none()
    
    if not message:
        raise ValueError("Message not found")
    
    reactions = message.reactions or {}
    user_id_str = str(user_id)
    
    if reaction_type in reactions and user_id_str in reactions[reaction_type]:
        reactions[reaction_type].remove(user_id_str)
        
        if not reactions[reaction_type]:
            del reactions[reaction_type]
    
    message.reactions = reactions
    attributes.flag_modified(message, "reactions")
    
    await db.commit()
    await db.refresh(message)
    
    return message