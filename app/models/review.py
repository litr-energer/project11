from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, DateTime, ForeignKey, Integer, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

class ReviewModel(Base):
    __tablename__ = "review"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    products_id: Mapped[Optional[int]] = mapped_column(ForeignKey("products.id"), nullable=True)
    listing_id: Mapped[Optional[int]] = mapped_column(ForeignKey("listing.id"), nullable=True)
    author_listing_id: Mapped[Optional[int]] = mapped_column(ForeignKey("author_listing.id"), nullable=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)