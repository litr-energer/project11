from typing import Optional
from pydantic import BaseModel, Field, validator
from decimal import Decimal


class ProductBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0)
    category: str = Field(..., max_length=100)
    image_url: Optional[str] = Field(None, max_length=500)
    
    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be greater than 0')
        return v


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    category: Optional[str] = Field(None, max_length=100)
    image_url: Optional[str] = Field(None, max_length=500)
    popularity: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    id: int
    popularity: int
    is_active: bool
    
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True