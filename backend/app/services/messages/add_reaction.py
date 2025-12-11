from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from sqlalchemy.orm import attributes

from app.models.messages import Message

async def add_reaction(
    db: AsyncSession,
    message_id: UUID,
    user_id: UUID,
    reaction_type: str
) -> Message:
    """add reaction to a message"""
    stmt = select(Message).where(Message.id == message_id)
    result = await db.execute(stmt)
    message = result.scalar_one_or_none()
    
    if not message:
        raise ValueError("Message not found")
    
    reactions = message.reactions or {}
    user_id_str = str(user_id)
    
    for emoji, user_ids in reactions.items():
        if user_id_str in user_ids:
            raise ValueError(
                f"User already has a reaction ('{emoji}') on this message")
    
    if reaction_type not in reactions:
        reactions[reaction_type] = []
    
    reactions[reaction_type].append(user_id_str)
        
    message.reactions = reactions
    attributes.flag_modified(message, "reactions")
    
    await db.commit()
    await db.refresh(message)
    
    return message
    
        
