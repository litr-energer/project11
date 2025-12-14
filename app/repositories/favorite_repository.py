from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.favorite import FavoriteModel
from app.repositories.base_repository import BaseRepository

class FavoriteRepository(BaseRepository[FavoriteModel]):
    def __init__(self, db: Session):
        super().__init__(db, FavoriteModel)
    
    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[FavoriteModel]:
        """Получить все избранное пользователя"""
        return (
            self.db.query(FavoriteModel)
            .filter(FavoriteModel.user_id == user_id)
            .order_by(FavoriteModel.added_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_one_by(self, user_id: int, **filters) -> Optional[FavoriteModel]:
        """Найти одну запись избранного по фильтрам"""
        query = self.db.query(FavoriteModel).filter(FavoriteModel.user_id == user_id)
        
        if filters.get("products_id"):
            query = query.filter(FavoriteModel.products_id == filters["products_id"])
        if filters.get("listing_id"):
            query = query.filter(FavoriteModel.listing_id == filters["listing_id"])
        if filters.get("author_listing_id"):
            query = query.filter(FavoriteModel.author_listing_id == filters["author_listing_id"])
        
        return query.first()
    
    def get_by_user_and_item(self, user_id: int, item_type: str, item_id: int) -> Optional[FavoriteModel]:
        """Получить избранное пользователя для конкретного товара"""
        filters = {}
        if item_type == "product":
            filters["products_id"] = item_id
        elif item_type == "listing":
            filters["listing_id"] = item_id
        elif item_type == "author_listing":
            filters["author_listing_id"] = item_id
        
        return self.get_one_by(user_id, **filters)
    
    def user_has_favorites(self, user_id: int) -> bool:
        """Проверить, есть ли у пользователя избранное"""
        return (
            self.db.query(FavoriteModel)
            .filter(FavoriteModel.user_id == user_id)
            .first() is not None
        )