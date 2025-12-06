from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Float, ForeignKey, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

class FavoriteModel(Base):
    __tablename__ = "favorite"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    products_id: Mapped[Optional[int]] = mapped_column(ForeignKey("products.id"), nullable=True)
    listing_id: Mapped[Optional[int]] = mapped_column(ForeignKey("listing.id"), nullable=True)
    author_listing_id: Mapped[Optional[int]] = mapped_column(ForeignKey("author_listing.id"), nullable=True)
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)