from pydantic import BaseModel, EmailStr
from typing import Optional
from decimal import Decimal
from datetime import datetime


class OrderBase(BaseModel):
    user_id: int
    total_amount: Decimal
    status: str = "pending"
    customer_name: str
    customer_email: EmailStr
    payment_method: str
    payment_data: Optional[str] = None


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    status: Optional[str] = None
    payment_data: Optional[str] = None


class Order(OrderBase):
    id: int
    creat_at: datetime
    
    class Config:
        from_attributes = True