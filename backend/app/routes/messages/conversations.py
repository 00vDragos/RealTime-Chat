from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from pydantic import BaseModel, Field

from app.db.dependencies import get_db
from app.services.conversation_service import ConversationService
from app.db.repositories.conversation_repo import ConversationRepository
from app.schemas.conversations import ConversationSummary, ConversationCreate
# import pentru from app.core.auth import get_current_user

# TEMPORARY AUTH MOCK (until real Google/JWT auth is implemented)
async def fake_get_current_user():
    class User:
        id = UUID("1eb0fa76-fad3-4dd2-9536-ec257c29bba3")
    return User()

class ConversationCreateRequest(BaseModel):
    participant_ids: list[UUID] = Field(default_factory=list)

router = APIRouter(prefix="/api/messages", tags=["messages"])

@router.get("/conversations", response_model=list[ConversationSummary])
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(fake_get_current_user),
):
    service = ConversationService(ConversationRepository(db))
    return await service.list_conversations(current_user.id)


@router.post("/new_conversation", response_model=ConversationCreate)
async def create_conversation(
    payload: ConversationCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(fake_get_current_user),
):

    service = ConversationService(ConversationRepository(db))
    return await service.create_conversation(current_user.id, payload.participant_ids)