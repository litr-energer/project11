from typing import Optional
from sqlalchemy.orm import Session
from app.models.roles import RoleModel
from app.repositories.repository import BaseRepository

class RoleRepository(BaseRepository[RoleModel]):
    def __init__(self, db: Session):
        super().__init__(RoleModel, db)
    
    def get_by_name(self, name: str) -> Optional[RoleModel]:
        return self.get_one_by(name=name)