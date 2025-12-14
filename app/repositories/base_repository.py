
from typing import TypeVar, Generic, Type, List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from app.database.database import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, db: Session, model: Type[ModelType]):
        self.db = db
        self.model = model

    def get(self, id: Any) -> Optional[ModelType]:
        """Получить запись по ID"""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        order_by: Optional[str] = None,
        order_desc: bool = False
    ) -> List[ModelType]:
        """Получить все записи с пагинацией и сортировкой"""
        query = self.db.query(self.model)
        
        if order_by:
            column = getattr(self.model, order_by, None)
            if column:
                if order_desc:
                    query = query.order_by(desc(column))
                else:
                    query = query.order_by(asc(column))
        
        return query.offset(skip).limit(limit).all()

    def get_by(
        self, 
        skip: int = 0, 
        limit: int = 100,
        **filters
    ) -> List[ModelType]:
        """Получить записи по фильтрам"""
        query = self.db.query(self.model)
        
        for attr, value in filters.items():
            if value is not None:
                if isinstance(value, list):
                    column = getattr(self.model, attr)
                    query = query.filter(column.in_(value))
                else:
                    query = query.filter(getattr(self.model, attr) == value)
        
        return query.offset(skip).limit(limit).all()

    def get_one_by(self, **filters) -> Optional[ModelType]:
        """Получить одну запись по фильтрам"""
        query = self.db.query(self.model)
        
        for attr, value in filters.items():
            if value is not None:
                query = query.filter(getattr(self.model, attr) == value)
        
        return query.first()

    def create(self, obj_in: Union[Dict[str, Any], ModelType]) -> ModelType:
        """Создать новую запись"""
        if isinstance(obj_in, dict):
            obj_in_data = obj_in
        else:
            obj_in_data = obj_in.dict() if hasattr(obj_in, 'dict') else obj_in.__dict__
        
        db_obj = self.model(**obj_in_data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, id: Any, obj_in: Union[Dict[str, Any], ModelType]) -> Optional[ModelType]:
        """Обновить запись"""
        db_obj = self.get(id)
        if not db_obj:
            return None
        
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True) if hasattr(obj_in, 'dict') else obj_in.__dict__
        
        for field, value in update_data.items():
            if hasattr(db_obj, field) and value is not None:
                setattr(db_obj, field, value)
        
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: Any) -> bool:
        """Удалить запись"""
        db_obj = self.get(id)
        if not db_obj:
            return False
        
        self.db.delete(db_obj)
        self.db.commit()
        return True

    def count(self, **filters) -> int:
        """Получить количество записей по фильтрам"""
        query = self.db.query(self.model)
        
        for attr, value in filters.items():
            if value is not None:
                query = query.filter(getattr(self.model, attr) == value)
        
        return query.count()

    def exists(self, **filters) -> bool:
        """Проверить существование записи по фильтрам"""
        return self.get_one_by(**filters) is not None
