from app.repositories.chat_message_repository import ChatMessageRepository
from app.services.service import BaseService
from app.models.chat_massage import ChatMessageModel

class ChatMessageService(BaseService[ChatMessageModel]):
    def __init__(self, chat_message_repository: ChatMessageRepository):
        super().__init__(chat_message_repository)
        self.chat_message_repository = chat_message_repository
    
    def get_user_messages(self, user_id: int, skip: int = 0, limit: int = 100):
        return self.chat_message_repository.get_by_user(user_id, skip, limit)
    
    def get_conversation(self, user_id: int, skip: int = 0, limit: int = 100):
        return self.chat_message_repository.get_conversation(user_id, skip, limit)
    
    def send_message(self, user_id: int, message_data: dict) -> ChatMessageModel:
        return self.chat_message_repository.create({**message_data, "user_id": user_id})