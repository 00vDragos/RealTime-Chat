from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from uuid import UUID

from app.db.dependencies import get_db
from app.schemas.messages import MessageRead, MessageReactionUpdate
from app.services.messages.add_reaction import add_reaction
from app.services.messages.change_reaction import change_reaction
from app.services.messages.remove_reaction import remove_reaction
from app.models.users import User
from app.services.auth.get_current_user import get_current_user
from app.websocket.events.message_reaction import handle_reaction

router = APIRouter()
security = HTTPBearer()

@router.post("/messages/{message_id}/reactions", 
             response_model=MessageRead,
             status_code=status.HTTP_201_CREATED,
             summary="Add reaction to a message")

async def add_message_reaction(
    message_id: UUID,
    reaction: MessageReactionUpdate,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: AsyncSession = Depends(get_db),
):
    current_user: User = await get_current_user(
        token=credentials.credentials,
        db=db,
    )
    
    try:
        message = await add_reaction(
            db=db,
            message_id=message_id,
            user_id=current_user.id,  
            reaction_type=reaction.reaction_type
        )
        
        await handle_reaction(
            conversation_id=message.conversation_id,
            message_id=message.id,
            user_id=current_user.id,
            reactions=message.reactions,
            event_type="added"
        )
        
        return message
    except ValueError as e:
        if "already has a reaction" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )

@router.put("/messages/{message_id}/reactions",
            response_model=MessageRead,
            status_code=status.HTTP_200_OK,
            summary="Change reaction on a message")
async def change_message_reaction(
    message_id: UUID,
    reaction: MessageReactionUpdate,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: AsyncSession = Depends(get_db),
):
    current_user: User = await get_current_user(
        token=credentials.credentials,
        db=db,
    )
    
    try:
        message = await change_reaction(
            db=db,
            message_id=message_id,
            user_id=current_user.id,
            new_reaction_type=reaction.reaction_type
        )
        
        await handle_reaction(
            conversation_id=message.conversation_id,
            message_id=message.id,
            user_id=current_user.id,
            reactions=message.reactions,
            event_type="changed"
        )
        
        return message
        
    except ValueError as e:
        if "has no current reaction" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            ) 

@router.delete(
    "/messages/{message_id}/reactions/{reaction_type}",
    response_model=MessageRead,
    status_code=status.HTTP_200_OK,
    summary="Remove reaction from message"
)
async def remove_message_reaction(
    message_id: UUID,
    reaction_type: str,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: AsyncSession = Depends(get_db),
):
    current_user: User = await get_current_user(
        token=credentials.credentials,
        db=db,
    )
    
    try:
        message = await remove_reaction(
            db=db,
            message_id=message_id,
            user_id=current_user.id,  
            reaction_type=reaction_type
        )
        
        await handle_reaction(
            conversation_id=message.conversation_id,
            message_id=message.id,
            user_id=current_user.id,
            reactions=message.reactions,
            event_type="removed"
        )
        
        return message
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
        