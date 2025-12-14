from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class ProductBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: Decimal
    category: str
    image_url: Optional[str] = None
    popularity: int = 0
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    popularity: Optional[int] = None
    is_active: Optional[bool] = None


class Product(ProductBase):
    id: int
    
    class Config:
        from_attributes = True