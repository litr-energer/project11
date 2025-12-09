from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime


class AuthorListingBase(BaseModel):
    title: str
    prise: Decimal
    topics_games: str
    image_url: Optional[str] = None
    user_id: int
    status: str = "active"


class AuthorListingCreate(AuthorListingBase):
    pass


class AuthorListingUpdate(BaseModel):
    title: Optional[str] = None
    prise: Optional[Decimal] = None
    topics_games: Optional[str] = None
    image_url: Optional[str] = None
    status: Optional[str] = None


class AuthorListing(AuthorListingBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True