from sqlalchemy.orm import Session
from app.models.orders import OrderModel
from app.repositories.repository import BaseRepository

class OrderRepository(BaseRepository[OrderModel]):
    def __init__(self, db: Session):
        super().__init__(OrderModel, db)
    
    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100):
        return self.db.query(self.model)\
            .filter(self.model.user_id == user_id)\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def get_by_status(self, status: str, skip: int = 0, limit: int = 100):
        return self.db.query(self.model)\
            .filter(self.model.status == status)\
            .offset(skip)\
            .limit(limit)\
            .all()