from pydantic import BaseModel
from datetime import datetime


class CartBase(BaseModel):
    user_id: int


class CartCreate(CartBase):
    pass


class Cart(CartBase):
    id: int
    creat_at: datetime
    update_ap: datetime
    
    class Config:
        from_attributes = True