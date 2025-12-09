from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.favorite_schema import Favorite, FavoriteCreate
from app.services.favorite_service import FavoriteService
from app.repositories.favorite_repository import FavoriteRepository
from app.exceptions.favorite_exceptions import (
    FavoriteNotFoundException,
    FavoriteAlreadyExistsException,
    FavoriteValidationException
)

# Создаем роутер - обратите внимание на переменную 'router' (не 'Router')
router = APIRouter(prefix="/favorites", tags=["favorites"])

def get_favorite_service(db: Session = Depends(get_db)) -> FavoriteService:
    favorite_repository = FavoriteRepository(db)
    return FavoriteService(favorite_repository)

@router.get("/user/{user_id}", response_model=List[Favorite])
def get_user_favorites(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    favorite_service: FavoriteService = Depends(get_favorite_service)
):
    return favorite_service.get_user_favorites(user_id, skip, limit)

@router.post("/", response_model=Favorite)
def add_to_favorites(
    favorite_data: FavoriteCreate,
    favorite_service: FavoriteService = Depends(get_favorite_service)
):
    try:
        # Проверяем, что указан хотя бы один тип товара
        if not any([favorite_data.products_id, favorite_data.listing_id, favorite_data.author_listing_id]):
            raise HTTPException(
                status_code=400, 
                detail="At least one of products_id, listing_id, or author_listing_id must be provided"
            )
        
        # Проверяем, не добавлен ли уже товар в избранное
        filters = {}
        if favorite_data.products_id:
            filters["products_id"] = favorite_data.products_id
        if favorite_data.listing_id:
            filters["listing_id"] = favorite_data.listing_id
        if favorite_data.author_listing_id:
            filters["author_listing_id"] = favorite_data.author_listing_id
        
        if favorite_service.is_item_favorited(favorite_data.user_id, **filters):
            raise FavoriteAlreadyExistsException(
                user_id=favorite_data.user_id,
                item_type="product" if favorite_data.products_id else "listing",
                item_id=favorite_data.products_id or favorite_data.listing_id or favorite_data.author_listing_id
            )
        
        return favorite_service.add_to_favorites(favorite_data.user_id, favorite_data.dict())
    except FavoriteAlreadyExistsException as e:
        raise e
    except Exception as e:
        raise FavoriteValidationException(detail=str(e))

@router.delete("/{favorite_id}")
def remove_from_favorites(
    favorite_id: int,
    favorite_service: FavoriteService = Depends(get_favorite_service)
):
    try:
        success = favorite_service.delete(favorite_id)
        return {"message": "Removed from favorites"}
    except FavoriteNotFoundException as e:
        raise e

@router.get("/check/{user_id}")
def check_if_favorited(
    user_id: int,
    product_id: int = None,
    listing_id: int = None,
    author_listing_id: int = None,
    favorite_service: FavoriteService = Depends(get_favorite_service)
):
    filters = {}
    if product_id:
        filters["products_id"] = product_id
    if listing_id:
        filters["listing_id"] = listing_id
    if author_listing_id:
        filters["author_listing_id"] = author_listing_id
    
    is_favorited = favorite_service.is_item_favorited(user_id, **filters)
    return {"is_favorited": is_favorited}