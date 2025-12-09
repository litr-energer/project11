from sqlalchemy.orm import Session
from app.models.chat_massage import ChatMessageModel
from app.repositories.repository import BaseRepository

class ChatMessageRepository(BaseRepository[ChatMessageModel]):
    def __init__(self, db: Session):
        super().__init__(ChatMessageModel, db)
    
    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100):
        return self.db.query(self.model)\
            .filter(self.model.user_id == user_id)\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def get_conversation(self, user_id: int, skip: int = 0, limit: int = 100):
        return self.db.query(self.model)\
            .filter(self.model.user_id == user_id)\
            .order_by(self.model.sent_at)\
            .offset(skip)\
            .limit(limit)\
            .all()