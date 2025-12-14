from app.repositories.favorite_repository import FavoriteRepository
from app.services.service import BaseService
from app.models.favorite import FavoriteModel

class FavoriteService(BaseService[FavoriteModel]):
    def __init__(self, favorite_repository: FavoriteRepository):
        super().__init__(favorite_repository)
        self.favorite_repository = favorite_repository
    
    def get_user_favorites(self, user_id: int, skip: int = 0, limit: int = 100):
        """Получить избранное пользователя с пагинацией"""
        return self.favorite_repository.get_by_user(user_id, skip, limit)
    
    def add_to_favorites(self, user_id: int, favorite_data: dict) -> FavoriteModel:
        """Добавить товар в избранное пользователя"""
        return self.favorite_repository.create({**favorite_data, "user_id": user_id})
    
    def is_item_favorited(self, user_id: int, **filters) -> bool:
        """Проверить, добавлен ли товар в избранное у пользователя"""
        favorite = self.favorite_repository.get_one_by(user_id=user_id, **filters)
        return favorite is not None
    
    def get_user_favorites_count(self, user_id: int) -> int:
        """Получить количество избранных товаров пользователя"""
        favorites = self.favorite_repository.get_by_user(user_id, 0, 1000)
        return len(favorites)
    
    def remove_from_favorites(self, user_id: int, **filters) -> bool:
        """Удалить товар из избранного пользователя"""
        favorite = self.favorite_repository.get_one_by(user_id=user_id, **filters)
        if favorite:
            return self.favorite_repository.delete(favorite.id)
        return False