from typing import Optional
from sqlalchemy.orm import Session
from app.models.users import UserModel
from app.repositories.repository import BaseRepository
from app.schemas.user_schema import UserCreate

class UserRepository(BaseRepository[UserModel]):
    def __init__(self, db: Session):
        super().__init__(UserModel, db)
    
    def get_by_email(self, email: str) -> Optional[UserModel]:
        return self.get_one_by(email=email)