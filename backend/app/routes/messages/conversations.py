from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from pydantic import BaseModel, Field

from app.db.dependencies import get_db
from app.services.conversation_service import ConversationService
from app.db.repositories.conversation_repo import ConversationRepository
from app.schemas.conversations import ConversationSummary
from app.services.auth.get_current_user import get_current_user as get_current_user_service


security = HTTPBearer()


# Dependency: extract Bearer token via HTTPBearer and return authenticated User
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: AsyncSession = Depends(get_db),
) :
    token = credentials.credentials
    user = await get_current_user_service(token=token, db=db)
    return user


class ConversationCreateRequest(BaseModel):
    participant_ids: list[UUID] = Field(default_factory=list)


router = APIRouter(prefix="/api/messages", tags=["messages"])


@router.get("/conversations", response_model=list[ConversationSummary])
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    service = ConversationService(ConversationRepository(db))
    return await service.list_conversations(current_user.id)



@router.post("/new_conversation", response_model=ConversationSummary)
async def create_conversation(
    payload: ConversationCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    repo = ConversationRepository(db)
    service = ConversationService(repo)

    # normalize participants (ensure current user included)
    participants = list(payload.participant_ids or [])
    if current_user.id not in participants:
        participants.append(current_user.id)

    # check duplicate conversation by exact participant set
    existing = await repo.find_conversation_by_participant_set(participants)
    if existing:
        raise HTTPException(status_code=409, detail="A conversation with the same participants already exists")

    return await service.create_conversation(current_user.id, payload.participant_ids)