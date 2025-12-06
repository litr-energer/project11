from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, ForeignKey, Integer, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.users import UserModel

class OrderItemModel(Base):
    __tablename__ = "order_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    products_id: Mapped[Optional[int]] = mapped_column(ForeignKey("products.id"), nullable=True)
    listing_id: Mapped[Optional[int]] = mapped_column(ForeignKey("listing.id"), nullable=True)
    author_listing_id: Mapped[Optional[int]] = mapped_column(ForeignKey("author_listing.id"), nullable=True)
    unit_price: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)