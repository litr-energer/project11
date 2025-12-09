from typing import Optional
from sqlalchemy.orm import Session
from app.models.carts import CartModel
from app.repositories.repository import BaseRepository

class CartRepository(BaseRepository[CartModel]):
    def __init__(self, db: Session):
        super().__init__(CartModel, db)
    
    def get_by_user(self, user_id: int) -> Optional[CartModel]:
        return self.get_one_by(user_id=user_id)