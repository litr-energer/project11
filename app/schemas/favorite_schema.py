from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FavoriteBase(BaseModel):
    user_id: int
    products_id: Optional[int] = None
    listing_id: Optional[int] = None
    author_listing_id: Optional[int] = None


class FavoriteCreate(FavoriteBase):
    pass


class Favorite(FavoriteBase):
    id: int
    added_at: datetime
    
    class Config:
        from_attributes = True