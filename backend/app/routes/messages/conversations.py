from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.dependencies import get_db
from app.services.conversation_service import ConversationService
from app.db.repositories.conversation_repo import ConversationRepository
from app.schemas.conversations import ConversationSummary
# import pentru from app.core.auth import get_current_user

# TEMPORARY AUTH MOCK (until real Google/JWT auth is implemented)
async def fake_get_current_user():
    class User:
        id = UUID("11111111-1111-1111-1111-111111111111")
    return User()

router = APIRouter(prefix="/api/messages", tags=["messages"])

@router.get("/conversations", response_model=list[ConversationSummary])
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(fake_get_current_user),
):
    service = ConversationService(ConversationRepository(db))
    return await service.list_conversations(current_user.id)


@router.post("/new_conversation", response_model=ConversationSummary)
async def create_conversation():
    pass