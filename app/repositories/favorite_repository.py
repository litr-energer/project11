from sqlalchemy.orm import Session
from app.models.favorite import FavoriteModel
from app.repositories.repository import BaseRepository

class FavoriteRepository(BaseRepository[FavoriteModel]):
    def __init__(self, db: Session):
        super().__init__(FavoriteModel, db)
    
    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100):
        return self.db.query(self.model)\
            .filter(self.model.user_id == user_id)\
            .offset(skip)\
            .limit(limit)\
            .all()