from sqlalchemy.orm import Session
from app.models.order_items import OrderItemModel
from app.repositories.repository import BaseRepository

class OrderItemRepository(BaseRepository[OrderItemModel]):
    def __init__(self, db: Session):
        super().__init__(OrderItemModel, db)
    
    def get_by_order(self, order_id: int, skip: int = 0, limit: int = 100):
        return self.db.query(self.model)\
            .filter(self.model.order_id == order_id)\
            .offset(skip)\
            .limit(limit)\
            .all()