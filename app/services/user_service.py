from typing import Optional
from passlib.context import CryptContext
from app.repositories.user_repository import UserRepository
from app.services.service import BaseService
from app.models.users import UserModel
from app.schemas.user_schema import UserCreate
from app.exceptions.user_exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidCredentialsException
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService(BaseService[UserModel]):
    def __init__(self, user_repository: UserRepository):
        super().__init__(user_repository)
        self.user_repository = user_repository
    
    def get(self, id: int) -> Optional[UserModel]:
        user = super().get(id)
        if not user:
            raise UserNotFoundException(user_id=id)
        return user
    
    def get_by_email(self, email: str) -> Optional[UserModel]:
        return self.user_repository.get_by_email(email)
    
    def create_user(self, user_data: UserCreate) -> UserModel:
        existing_user = self.get_by_email(user_data.email)
        if existing_user:
            raise UserAlreadyExistsException(email=user_data.email)
        
        
        hashed_password = pwd_context.hash(user_data.password)
        user_dict = user_data.dict(exclude={"password"})
        user_dict["hashed_password"] = hashed_password
        
        return self.user_repository.create(user_dict)
    
    def authenticate_user(self, email: str, password: str) -> Optional[UserModel]:
        user = self.get_by_email(email)
        if not user:
            raise InvalidCredentialsException()
        
        if not pwd_context.verify(password, user.hashed_password):
            raise InvalidCredentialsException()
        
        return user
    
    def update_user(self, user_id: int, update_data: dict) -> Optional[UserModel]:
        # Проверяем существование пользователя
        self.get(user_id)
        
        # Проверяем, не используется ли email другим пользователем
        if "email" in update_data:
            existing_user = self.get_by_email(update_data["email"])
            if existing_user and existing_user.id != user_id:
                raise UserAlreadyExistsException(email=update_data["email"])
        
        # Хешируем пароль, если он предоставлен
        if "password" in update_data:
            update_data["hashed_password"] = pwd_context.hash(update_data.pop("password"))
        
        return self.user_repository.update(user_id, update_data)
    
    def delete(self, id: int) -> bool:
        # Проверяем существование пользователя
        self.get(id)
        return super().delete(id)