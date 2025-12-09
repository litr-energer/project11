from typing import Generic, TypeVar, List, Optional, Dict, Any
from app.repositories.repository import BaseRepository

ModelType = TypeVar("ModelType")

class BaseService(Generic[ModelType]):
    def __init__(self, repository: BaseRepository[ModelType]):
        self.repository = repository

    def get(self, id: int) -> Optional[ModelType]:
        return self.repository.get(id)

    def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        order_by: Optional[str] = None,
        order_direction: str = "asc"
    ) -> List[ModelType]:
        return self.repository.get_all(skip, limit, order_by, order_direction)

    def create(self, obj_in: Dict[str, Any]) -> ModelType:
        return self.repository.create(obj_in)

    def update(self, id: int, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        return self.repository.update(id, obj_in)

    def delete(self, id: int) -> bool:
        return self.repository.delete(id)

    def filter_by(self, **filters) -> List[ModelType]:
        return self.repository.filter_by(**filters)

    def get_one_by(self, **filters) -> Optional[ModelType]:
        return self.repository.get_one_by(**filters)