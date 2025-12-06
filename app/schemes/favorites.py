from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class FavoriteBase(BaseModel):
    user_id: int = Field(..., gt=0)
    products_id: Optional[int] = Field(None, gt=0)
    listing_id: Optional[int] = Field(None, gt=0)
    author_listing_id: Optional[int] = Field(None, gt=0)
    
    class Config:
        arbitrary_types_allowed = True


class FavoriteCreate(FavoriteBase):
    pass


class FavoriteResponse(FavoriteBase):
    id: int
    added_at: datetime
    
    class Config:
        from_attributes = True


class FavoriteCheckRequest(BaseModel):
    user_id: int
    products_id: Optional[int] = None
    listing_id: Optional[int] = None
    author_listing_id: Optional[int] = None


class FavoriteRemoveRequest(BaseModel):
    products_id: Optional[int] = None
    listing_id: Optional[int] = None
    author_listing_id: Optional[int] = None