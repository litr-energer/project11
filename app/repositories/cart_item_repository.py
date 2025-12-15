from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.cart_items import CartItemModel
from app.repositories.repository import BaseRepository


class CartItemRepository(BaseRepository[CartItemModel]):
    def __init__(self, db: Session):
        super().__init__(CartItemModel, db)
    
    def get_by_cart_id(self, cart_id: int, skip: int = 0, limit: int = 100) -> List[CartItemModel]:
        return self.db.query(self.model)\
            .filter(self.model.cart_id == cart_id)\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def get_by_cart_and_item(self, cart_id: int, item_type: str, item_id: int) -> Optional[CartItemModel]:
        filters = {
            "cart_id": cart_id,
            item_type + "_id": item_id  # Например: product_id=5 или listing_id=3
        }
        return self.get_one_by(**filters)