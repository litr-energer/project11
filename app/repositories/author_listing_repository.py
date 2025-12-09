from sqlalchemy.orm import Session
from app.models.author_listing import AuthorListingModel
from app.repositories.repository import BaseRepository

class AuthorListingRepository(BaseRepository[AuthorListingModel]):
    def __init__(self, db: Session):
        super().__init__(AuthorListingModel, db)
    
    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100):
        return self.db.query(self.model)\
            .filter(self.model.user_id == user_id)\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def get_by_topic(self, topic: str, skip: int = 0, limit: int = 100):
        return self.db.query(self.model)\
            .filter(self.model.topics_games == topic)\
            .offset(skip)\
            .limit(limit)\
            .all()