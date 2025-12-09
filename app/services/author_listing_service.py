from app.repositories.author_listing_repository import AuthorListingRepository
from app.services.service import BaseService
from app.models.author_listing import AuthorListingModel

class AuthorListingService(BaseService[AuthorListingModel]):
    def __init__(self, author_listing_repository: AuthorListingRepository):
        super().__init__(author_listing_repository)
        self.author_listing_repository = author_listing_repository
    
    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100):
        return self.author_listing_repository.get_by_user(user_id, skip, limit)
    
    def get_by_topic(self, topic: str, skip: int = 0, limit: int = 100):
        return self.author_listing_repository.get_by_topic(topic, skip, limit)
    
    def get_active_listings(self, skip: int = 0, limit: int = 100):
        return self.author_listing_repository.filter_by(status="active")