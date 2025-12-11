from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from pydantic import BaseModel, Field

from app.db.dependencies import get_db, get_current_user_id
from app.services.conversation_service import ConversationService
from app.db.repositories.conversation_repo import ConversationRepository
from app.schemas.conversations import ConversationSummary, ConversationCreate
from app.websocket.manager import manager


class ConversationCreateRequest(BaseModel):
    participant_ids: list[UUID] = Field(default_factory=list)

router = APIRouter(prefix="/api/messages", tags=["messages"])

@router.get("/conversations", response_model=list[ConversationSummary])
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    service = ConversationService(ConversationRepository(db))
    return await service.list_conversations(user_id)


@router.post("/new_conversation", response_model=ConversationCreate)
async def create_conversation(
    payload: ConversationCreateRequest,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):

    service = ConversationService(ConversationRepository(db))
    summary = await service.create_conversation(user_id, payload.participant_ids)

    # Notify participants via websocket so the conversation appears for them immediately
    participant_ids = summary.get("participantIds", [])
    try:
        await manager.broadcast(
            participant_ids,
            {
                "event": "conversation_created",
                "conversation": summary,
            },
        )
    except Exception:
        # Do not fail the API if websockets broadcasting fails
        pass

    return summary