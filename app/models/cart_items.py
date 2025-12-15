from datetime import datetime
from sqlalchemy import String, Float, ForeignKey, Integer, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base
from .carts import CartModel


class CartItemModel(Base):
    __tablename__ = "cart_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cart_id: Mapped[int] = mapped_column(ForeignKey("carts.id"), nullable=False)
    item_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'product', 'listing', 'author_listing'
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("listing.id"), nullable=True)
    author_listing_id: Mapped[int] = mapped_column(ForeignKey("author_listing.id"), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Связи
    cart: Mapped["CartModel"] = relationship("CartModel", back_populates="items")
    product = relationship("ProductModel", backref="cart_items")
    listing = relationship("ListingModel", backref="cart_items")
    author_listing = relationship("AuthorListingModel", backref="cart_items")