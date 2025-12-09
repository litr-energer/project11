from typing import Optional
from app.repositories.role_repository import RoleRepository
from app.services.service import BaseService
from app.models.roles import RoleModel


class RoleService(BaseService[RoleModel]):
    def __init__(self, role_repository: RoleRepository):
        super().__init__(role_repository)
        self.role_repository = role_repository
    
    def get_by_name(self, name: str) -> Optional[RoleModel]:
        return self.role_repository.get_by_name(name)