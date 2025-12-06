from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Float, ForeignKey, Integer, DateTime, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

class ChatMessageModel(Base):
    __tablename__ = "chat_massage"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    massage_text: Mapped[str] = mapped_column(Text, nullable=False)
    massage_type: Mapped[str] = mapped_column(String(50), nullable=False)
    is_from_user: Mapped[bool] = mapped_column(Boolean, default=True)
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)