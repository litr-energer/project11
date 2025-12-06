from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Float, ForeignKey, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.roles import RoleModel

class CartModel(Base):
    __tablename__ = "carts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    creat_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    update_ap: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)