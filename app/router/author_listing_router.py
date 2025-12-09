from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas import AuthorListing, AuthorListingCreate, AuthorListingUpdate
from app.services.author_listing_service import AuthorListingService
from app.repositories.author_listing_repository import AuthorListingRepository

router = APIRouter(prefix="/author-listings", tags=["author-listings"])

def get_author_listing_service(db: Session = Depends(get_db)) -> AuthorListingService:
    author_listing_repository = AuthorListingRepository(db)
    return AuthorListingService(author_listing_repository)

@router.get("/", response_model=List[AuthorListing])
def get_author_listings(
    skip: int = 0,
    limit: int = 100,
    user_id: int = None,
    topic: str = None,
    active_only: bool = True,
    author_listing_service: AuthorListingService = Depends(get_author_listing_service)
):
    if user_id:
        return author_listing_service.get_by_user(user_id, skip, limit)
    elif topic:
        return author_listing_service.get_by_topic(topic, skip, limit)
    elif active_only:
        return author_listing_service.get_active_listings(skip, limit)
    else:
        return author_listing_service.get_all(skip, limit)

@router.get("/{listing_id}", response_model=AuthorListing)
def get_author_listing(
    listing_id: int,
    author_listing_service: AuthorListingService = Depends(get_author_listing_service)
):
    listing = author_listing_service.get(listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Author listing not found")
    return listing

@router.post("/", response_model=AuthorListing)
def create_author_listing(
    listing_data: AuthorListingCreate,
    author_listing_service: AuthorListingService = Depends(get_author_listing_service)
):
    return author_listing_service.create(listing_data.dict())

@router.put("/{listing_id}", response_model=AuthorListing)
def update_author_listing(
    listing_id: int,
    listing_data: AuthorListingUpdate,
    author_listing_service: AuthorListingService = Depends(get_author_listing_service)
):
    listing = author_listing_service.get(listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Author listing not found")
    
    return author_listing_service.update(listing_id, listing_data.dict(exclude_unset=True))

@router.delete("/{listing_id}")
def delete_author_listing(
    listing_id: int,
    author_listing_service: AuthorListingService = Depends(get_author_listing_service)
):
    success = author_listing_service.delete(listing_id)
    if not success:
        raise HTTPException(status_code=404, detail="Author listing not found")
    return {"message": "Author listing deleted successfully"}