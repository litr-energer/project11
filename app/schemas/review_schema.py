from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ReviewBase(BaseModel):
    user_id: int
    products_id: Optional[int] = None
    listing_id: Optional[int] = None
    author_listing_id: Optional[int] = None
    rating: int
    comment: Optional[str] = None
    is_verified: bool = False


class ReviewCreate(ReviewBase):
    pass


class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    comment: Optional[str] = None
    is_verified: Optional[bool] = None


class Review(ReviewBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True