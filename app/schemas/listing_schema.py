from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime


class ListingBase(BaseModel):
    title: str
    price: Decimal
    game_topic: str
    image_url: Optional[str] = None
    user_id: int
    status: str = "active"


class ListingCreate(ListingBase):
    pass


class ListingUpdate(BaseModel):
    title: Optional[str] = None
    price: Optional[Decimal] = None
    game_topic: Optional[str] = None
    image_url: Optional[str] = None
    status: Optional[str] = None


class Listing(ListingBase):
    id: int
    create_at: datetime
    
    class Config:
        from_attributes = True