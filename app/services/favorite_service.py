from app.repositories.favorite_repository import FavoriteRepository
from app.services.service import BaseService
from app.models.favorite import FavoriteModel

class FavoriteService(BaseService[FavoriteModel]):
    def __init__(self, favorite_repository: FavoriteRepository):
        super().__init__(favorite_repository)
        self.favorite_repository = favorite_repository
    
    def get_user_favorites(self, user_id: int, skip: int = 0, limit: int = 100):
        return self.favorite_repository.get_by_user(user_id, skip, limit)
    
    def add_to_favorites(self, user_id: int, favorite_data: dict) -> FavoriteModel:
        return self.favorite_repository.create({**favorite_data, "user_id": user_id})
    
    def is_item_favorited(self, user_id: int, **filters) -> bool:
        favorite = self.favorite_repository.get_one_by(user_id=user_id, **filters)
        return favorite is not None