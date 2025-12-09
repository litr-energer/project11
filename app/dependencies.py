from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository

def get_current_user_service(db: Session = Depends(get_db)) -> UserService:
    user_repository = UserRepository(db)
    return UserService(user_repository)