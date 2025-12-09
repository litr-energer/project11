from sqlalchemy.orm import Session
from app.models.review import ReviewModel
from app.repositories.repository import BaseRepository

class ReviewRepository(BaseRepository[ReviewModel]):
    def __init__(self, db: Session):
        super().__init__(ReviewModel, db)
    
    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100):
        return self.db.query(self.model)\
            .filter(self.model.user_id == user_id)\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def get_by_product(self, product_id: int, skip: int = 0, limit: int = 100):
        return self.db.query(self.model)\
            .filter(self.model.products_id == product_id)\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def get_by_rating(self, min_rating: int = 1, max_rating: int = 5, skip: int = 0, limit: int = 100):
        return self.db.query(self.model)\
            .filter(self.model.rating >= min_rating, self.model.rating <= max_rating)\
            .offset(skip)\
            .limit(limit)\
            .all()