from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, DateTime, ForeignKey, Integer, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column, relationship 
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.users import UserModel

class AuthorListingModel(Base):
    __tablename__ = "author_listing"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    prise: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    topics_games: Mapped[str] = mapped_column(String(100), nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")