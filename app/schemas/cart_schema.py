from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class ItemType(str, Enum):
    PRODUCT = "product"
    LISTING = "listing"
    AUTHOR_LISTING = "author_listing"


# ВРЕМЕННО: упрощенная схема для отладки
class CartItemCreate(BaseModel):
    item_type: ItemType
    product_id: Optional[int] = None
    listing_id: Optional[int] = None
    author_listing_id: Optional[int] = None
    quantity: int = 1
    price: float = 0.0


class CartItemUpdate(BaseModel):
    quantity: Optional[int] = Field(None, ge=1)


class CartItem(BaseModel):
    id: int
    cart_id: int
    item_type: ItemType
    product_id: Optional[int] = None
    listing_id: Optional[int] = None
    author_listing_id: Optional[int] = None
    quantity: int
    price: float
    created_at: datetime
    
    class Config:
        from_attributes = True


# Остальные схемы
class CartBase(BaseModel):
    user_id: int


class CartCreate(CartBase):
    pass


class Cart(CartBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True