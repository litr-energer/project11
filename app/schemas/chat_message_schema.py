from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChatMessageBase(BaseModel):
    user_id: int
    massage_text: str
    massage_type: str
    is_from_user: bool = True


class ChatMessageCreate(ChatMessageBase):
    pass


class ChatMessageUpdate(BaseModel):
    massage_text: Optional[str] = None
    massage_type: Optional[str] = None
    is_from_user: Optional[bool] = None


class ChatMessage(ChatMessageBase):
    id: int
    sent_at: datetime
    
    class Config:
        from_attributes = True