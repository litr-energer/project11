from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CartItemBase(BaseModel):
    cart_id: int
    product_id: Optional[int] = None
    listing_id: Optional[int] = None
    author_listing_id: Optional[int] = None
    quantity: int = 1


class CartItemCreate(CartItemBase):
    pass


class CartItemUpdate(BaseModel):
    quantity: Optional[int] = None


class CartItem(CartItemBase):
    id: int
    added_at: datetime
    
    class Config:
        from_attributes = True