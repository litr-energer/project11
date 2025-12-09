from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db  # Теперь импорт работает
from app.schemas.role_schema import Role, RoleCreate, RoleUpdate
from app.services.role_service import RoleService
from app.repositories.role_repository import RoleRepository
from app.exceptions.role_exceptions import (
    RoleNotFoundException,
    RoleAlreadyExistsException,
    RoleValidationException
)

router = APIRouter(prefix="/roles", tags=["roles"])

def get_role_service(db: Session = Depends(get_db)) -> RoleService:
    role_repository = RoleRepository(db)
    return RoleService(role_repository)

@router.get("/", response_model=List[Role])
def get_roles(
    skip: int = 0,
    limit: int = 100,
    role_service: RoleService = Depends(get_role_service)
):
    return role_service.get_all(skip, limit)

@router.get("/{role_id}", response_model=Role)
def get_role(
    role_id: int,
    role_service: RoleService = Depends(get_role_service)
):
    try:
        return role_service.get(role_id)
    except RoleNotFoundException as e:
        raise e

@router.post("/", response_model=Role)
def create_role(
    role_data: RoleCreate,
    role_service: RoleService = Depends(get_role_service)
):
    try:
        # Проверяем, существует ли роль с таким именем
        existing_role = role_service.get_by_name(role_data.name)
        if existing_role:
            raise RoleAlreadyExistsException(role_name=role_data.name)
        return role_service.create(role_data.dict())
    except RoleAlreadyExistsException as e:
        raise e
    except Exception as e:
        raise RoleValidationException(detail=str(e))

@router.put("/{role_id}", response_model=Role)
def update_role(
    role_id: int,
    role_data: RoleUpdate,
    role_service: RoleService = Depends(get_role_service)
):
    try:
        role = role_service.get(role_id)
        return role_service.update(role_id, role_data.dict(exclude_unset=True))
    except RoleNotFoundException as e:
        raise e
    except Exception as e:
        raise RoleValidationException(detail=str(e))

@router.delete("/{role_id}")
def delete_role(
    role_id: int,
    role_service: RoleService = Depends(get_role_service)
):
    try:
        success = role_service.delete(role_id)
        return {"message": "Role deleted successfully"}
    except RoleNotFoundException as e:
        raise e