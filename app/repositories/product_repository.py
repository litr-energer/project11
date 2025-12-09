from sqlalchemy.orm import Session
from app.models.products import ProductModel
from app.repositories.repository import BaseRepository

class ProductRepository(BaseRepository[ProductModel]):
    def __init__(self, db: Session):
        super().__init__(ProductModel, db)
    
    def get_by_category(self, category: str, skip: int = 0, limit: int = 100):
        return self.db.query(self.model)\
            .filter(self.model.category == category)\
            .offset(skip)\
            .limit(limit)\
            .all()