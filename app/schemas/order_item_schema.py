from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class OrderItemBase(BaseModel):
    order_id: int
    products_id: Optional[int] = None
    listing_id: Optional[int] = None
    author_listing_id: Optional[int] = None
    unit_price: Decimal
    quantity: int = 1


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemUpdate(BaseModel):
    quantity: Optional[int] = None


class OrderItem(OrderItemBase):
    id: int
    
    class Config:
        from_attributes = True