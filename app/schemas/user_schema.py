from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserBase(BaseModel):
    name: str
    email: EmailStr
    role_id: int


class UserCreate(UserBase):
    name: str
    email: EmailStr
    password: str
    role_id: Optional[int] = Field(default=2)  # Установить значение по умолчанию


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role_id: Optional[int] = None


class User(UserBase):
    id: int
    
    class Config:
        from_attributes = True