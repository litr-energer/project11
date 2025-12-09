from app.repositories.listing_repository import ListingRepository
from app.services.service import BaseService
from app.models.listing import ListingModel

class ListingService(BaseService[ListingModel]):
    def __init__(self, listing_repository: ListingRepository):
        super().__init__(listing_repository)
        self.listing_repository = listing_repository
    
    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100):
        return self.listing_repository.get_by_user(user_id, skip, limit)
    
    def get_by_game_topic(self, game_topic: str, skip: int = 0, limit: int = 100):
        return self.listing_repository.get_by_game_topic(game_topic, skip, limit)
    
    def get_active_listings(self, skip: int = 0, limit: int = 100):
        return self.listing_repository.filter_by(status="active")