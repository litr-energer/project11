from sqlalchemy.orm import Session
from app.models.listing import ListingModel
from app.repositories.repository import BaseRepository

class ListingRepository(BaseRepository[ListingModel]):
    def __init__(self, db: Session):
        super().__init__(ListingModel, db)
    
    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100):
        return self.db.query(self.model)\
            .filter(self.model.user_id == user_id)\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def get_by_game_topic(self, game_topic: str, skip: int = 0, limit: int = 100):
        return self.db.query(self.model)\
            .filter(self.model.game_topic == game_topic)\
            .offset(skip)\
            .limit(limit)\
            .all()