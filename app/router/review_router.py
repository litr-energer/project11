from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas import Review, ReviewCreate, ReviewUpdate
from app.services.review_service import ReviewService
from app.repositories.review_repository import ReviewRepository

router = APIRouter(prefix="/reviews", tags=["reviews"])

def get_review_service(db: Session = Depends(get_db)) -> ReviewService:
    review_repository = ReviewRepository(db)
    return ReviewService(review_repository)

@router.get("/", response_model=List[Review])
def get_reviews(
    skip: int = 0,
    limit: int = 100,
    user_id: int = None,
    product_id: int = None,
    min_rating: int = None,
    max_rating: int = None,
    verified_only: bool = False,
    review_service: ReviewService = Depends(get_review_service)
):
    if user_id:
        return review_service.get_by_user(user_id, skip, limit)
    elif product_id:
        return review_service.get_by_product(product_id, skip, limit)
    elif min_rating is not None or max_rating is not None:
        min_rating = min_rating or 1
        max_rating = max_rating or 5
        return review_service.get_by_rating_range(min_rating, max_rating, skip, limit)
    elif verified_only:
        return review_service.get_verified_reviews(skip, limit)
    else:
        return review_service.get_all(skip, limit)

@router.get("/{review_id}", response_model=Review)
def get_review(
    review_id: int,
    review_service: ReviewService = Depends(get_review_service)
):
    review = review_service.get(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

@router.post("/", response_model=Review)
def create_review(
    review_data: ReviewCreate,
    review_service: ReviewService = Depends(get_review_service)
):
    # Проверяем, что указан хотя бы один тип товара
    if not any([review_data.products_id, review_data.listing_id, review_data.author_listing_id]):
        raise HTTPException(
            status_code=400, 
            detail="At least one of products_id, listing_id, or author_listing_id must be provided"
        )
    
    # Проверяем рейтинг
    if not 1 <= review_data.rating <= 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    return review_service.create(review_data.dict())

@router.put("/{review_id}", response_model=Review)
def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    review_service: ReviewService = Depends(get_review_service)
):
    review = review_service.get(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    if review_data.rating and not 1 <= review_data.rating <= 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    return review_service.update(review_id, review_data.dict(exclude_unset=True))

@router.delete("/{review_id}")
def delete_review(
    review_id: int,
    review_service: ReviewService = Depends(get_review_service)
):
    success = review_service.delete(review_id)
    if not success:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"message": "Review deleted successfully"}

@router.get("/average-rating")
def get_average_rating(
    product_id: int = None,
    listing_id: int = None,
    author_listing_id: int = None,
    review_service: ReviewService = Depends(get_review_service)
):
    filters = {}
    if product_id:
        filters["products_id"] = product_id
    if listing_id:
        filters["listing_id"] = listing_id
    if author_listing_id:
        filters["author_listing_id"] = author_listing_id
    
    average = review_service.calculate_average_rating(**filters)
    return {"average_rating": round(average, 2)}

@router.patch("/{review_id}/verify")
def verify_review(
    review_id: int,
    review_service: ReviewService = Depends(get_review_service)
):
    review = review_service.get(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    review_service.update(review_id, {"is_verified": True})
    return {"message": "Review verified successfully"}