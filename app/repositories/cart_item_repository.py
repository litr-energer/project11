from sqlalchemy.orm import Session
from app.models.cart_items import CartItemModel
from app.repositories.repository import BaseRepository

class CartItemRepository(BaseRepository[CartItemModel]):
    def __init__(self, db: Session):
        super().__init__(CartItemModel, db)
    
    def get_by_cart(self, cart_id: int, skip: int = 0, limit: int = 100):
        return self.db.query(self.model)\
            .filter(self.model.cart_id == cart_id)\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def get_by_product(self, product_id: int, skip: int = 0, limit: int = 100):
        return self.db.query(self.model)\
            .filter(self.model.product_id == product_id)\
            .offset(skip)\
            .limit(limit)\
            .all()