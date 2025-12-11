import uuid
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class MessageBase(BaseModel):
    conversation_id: uuid.UUID
    sender_id: uuid.UUID
    body: str


class MessageCreate(MessageBase):
    pass

class MessageReactionSummary(BaseModel):
    reaction_type: str
    count: int
    user_ids: List[str]
    has_current_user: bool = False
    
class MessageReactionUpdate(BaseModel):
    reaction_type: str

class MessageRead(MessageBase):
    id: uuid.UUID
    sender_name: Optional[str] = None
    created_at: datetime
    delivered_at: Optional[Dict[str, Any]] = None
    seen_at: Optional[Dict[str, Any]] = None
    edited_at: Optional[datetime] = None
    deleted_for_everyone: bool = False
    reactions: Optional[Dict[str, List[str]]] = Field(default_factory=dict)

    class Config:
        orm_mode = True
    
    def get_reactions_summary(self, current_user_id: Optional[str] = None) -> List[MessageReactionSummary]:
        "Convert reactions list to summary list"
        if not self.reactions:
            return []
        
        summary = []
        for emoji, user_ids in self.reactions.items():
            summary.append(MessageReactionSummary(
                reaction_type=emoji,
                count=len(user_ids),
                user_ids=user_ids,
                has_current_user=current_user_id in user_ids if current_user_id else False
            ))
        return summary
