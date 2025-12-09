from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
# Исправленный импорт - из модуля listing_schema
from app.schemas.listing_schema import Listing, ListingCreate, ListingUpdate
from app.services.listing_service import ListingService
from app.repositories.listing_repository import ListingRepository
from app.exceptions.listing_exceptions import (
    ListingNotFoundException,
    ListingValidationException,
    ListingInactiveException
)

router = APIRouter(prefix="/listings", tags=["listings"])

def get_listing_service(db: Session = Depends(get_db)) -> ListingService:
    listing_repository = ListingRepository(db)
    return ListingService(listing_repository)

@router.get("/", response_model=List[Listing])
def get_listings(
    skip: int = 0,
    limit: int = 100,
    user_id: int = None,
    game_topic: str = None,
    active_only: bool = True,
    listing_service: ListingService = Depends(get_listing_service)
):
    if user_id:
        return listing_service.get_by_user(user_id, skip, limit)
    elif game_topic:
        return listing_service.get_by_game_topic(game_topic, skip, limit)
    elif active_only:
        return listing_service.get_active_listings(skip, limit)
    else:
        return listing_service.get_all(skip, limit)

@router.get("/{listing_id}", response_model=Listing)
def get_listing(
    listing_id: int,
    listing_service: ListingService = Depends(get_listing_service)
):
    try:
        return listing_service.get(listing_id)
    except ListingNotFoundException as e:
        raise e

@router.post("/", response_model=Listing)
def create_listing(
    listing_data: ListingCreate,
    listing_service: ListingService = Depends(get_listing_service)
):
    try:
        return listing_service.create(listing_data.dict())
    except Exception as e:
        raise ListingValidationException(detail=str(e))

@router.put("/{listing_id}", response_model=Listing)
def update_listing(
    listing_id: int,
    listing_data: ListingUpdate,
    listing_service: ListingService = Depends(get_listing_service)
):
    try:
        listing = listing_service.get(listing_id)
        return listing_service.update(listing_id, listing_data.dict(exclude_unset=True))
    except ListingNotFoundException as e:
        raise e
    except Exception as e:
        raise ListingValidationException(detail=str(e))

@router.delete("/{listing_id}")
def delete_listing(
    listing_id: int,
    listing_service: ListingService = Depends(get_listing_service)
):
    try:
        success = listing_service.delete(listing_id)
        return {"message": "Listing deleted successfully"}
    except ListingNotFoundException as e:
        raise e

@router.patch("/{listing_id}/status")
def update_listing_status(
    listing_id: int,
    status: str,
    listing_service: ListingService = Depends(get_listing_service)
):
    try:
        listing = listing_service.get(listing_id)
        listing_service.update(listing_id, {"status": status})
        return {"message": f"Listing status updated to {status}"}
    except ListingNotFoundException as e:
        raise e