
# app/api/review.py - исправленная версия
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_, or_, desc, asc, case
from datetime import datetime, timedelta
import traceback

from app.database.database import get_async_session
from app.models.review import ReviewModel
from app.models.products import ProductModel
from app.models.listing import ListingModel
from app.models.author_listing import AuthorListingModel
from app.models.users import UserModel

router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"]
)


@router.get("/", response_model=List[dict])
async def get_reviews(
    user_id: Optional[int] = Query(None, description="Фильтр по пользователю"),
    product_id: Optional[int] = Query(None, description="Фильтр по товару"),
    listing_id: Optional[int] = Query(None, description="Фильтр по листингу"),
    author_listing_id: Optional[int] = Query(None, description="Фильтр по авторскому листингу"),
    min_rating: Optional[int] = Query(None, ge=1, le=5, description="Минимальный рейтинг"),
    max_rating: Optional[int] = Query(None, ge=1, le=5, description="Максимальный рейтинг"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    order_by: str = Query("newest", description="Сортировка: newest, oldest, highest_rating, lowest_rating"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить список отзывов с фильтрацией и пагинацией
    """
    try:
        query = select(ReviewModel)
        
        # Применяем фильтры
        if user_id:
            query = query.where(ReviewModel.user_id == user_id)
        
        if product_id:
            query = query.where(ReviewModel.product_id == product_id)
        
        if listing_id:
            query = query.where(ReviewModel.listing_id == listing_id)
        
        if author_listing_id:
            query = query.where(ReviewModel.author_listing_id == author_listing_id)
        
        if min_rating is not None:
            query = query.where(ReviewModel.rating >= min_rating)
        
        if max_rating is not None:
            query = query.where(ReviewModel.rating <= max_rating)
        
        # Сортировка
        if order_by == "oldest":
            query = query.order_by(asc(ReviewModel.created_at))
        elif order_by == "highest_rating":
            query = query.order_by(desc(ReviewModel.rating))
        elif order_by == "lowest_rating":
            query = query.order_by(asc(ReviewModel.rating))
        else:  # "newest" по умолчанию
            query = query.order_by(desc(ReviewModel.created_at))
        
        # Пагинация
        query = query.offset(skip).limit(limit)
        
        result = await session.execute(query)
        reviews = result.scalars().all()
        
        return [review.to_dict() for review in reviews]
        
    except Exception as e:
        print(f"Error in get_reviews: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{review_id}", response_model=dict)
async def get_review(
    review_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить отзыв по ID
    """
    try:
        query = select(ReviewModel).where(ReviewModel.id == review_id)
        result = await session.execute(query)
        review = result.scalar_one_or_none()
        
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )
        
        return review.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_review: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: dict,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Создать новый отзыв
    """
    try:
        # Проверяем обязательные поля
        required_fields = ['user_id', 'rating']
        for field in required_fields:
            if field not in review_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required field: {field}"
                )
        
        # Проверяем, что указан хотя бы один ID контента
        content_fields = ['product_id', 'listing_id', 'author_listing_id']
        if not any(field in review_data for field in content_fields):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one content ID must be specified"
            )
        
        # Проверяем рейтинг
        rating = review_data['rating']
        if rating < 1 or rating > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating must be between 1 and 5"
            )
        
        # Проверяем существование пользователя
        user_query = select(UserModel).where(UserModel.id == review_data['user_id'])
        user_result = await session.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Создаем отзыв
        review = ReviewModel(
            user_id=review_data['user_id'],
            product_id=review_data.get('product_id'),
            listing_id=review_data.get('listing_id'),
            author_listing_id=review_data.get('author_listing_id'),
            rating=rating,
            title=review_data.get('title'),
            comment=review_data.get('comment'),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        session.add(review)
        await session.commit()
        await session.refresh(review)
        
        return {
            **review.to_dict(),
            "message": "Review created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in create_review: {e}")
        print(traceback.format_exc())
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


# Упрощенные версии других функций без поля is_approved
@router.get("/product/{product_id}/statistics", response_model=dict)
async def get_product_review_statistics(
    product_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить статистику отзывов для товара
    """
    try:
        # Получаем все отзывы для товара
        reviews_query = select(ReviewModel).where(
            ReviewModel.product_id == product_id
        )
        reviews_result = await session.execute(reviews_query)
        reviews = reviews_result.scalars().all()
        
        total_reviews = len(reviews)
        
        if total_reviews == 0:
            return {
                "product_id": product_id,
                "total_reviews": 0,
                "average_rating": 0,
                "rating_distribution": {},
                "has_reviews": False
            }
        
        # Средний рейтинг
        total_rating = sum(review.rating for review in reviews)
        average_rating = total_rating / total_reviews
        
        # Распределение по рейтингам
        rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in reviews:
            rating_distribution[review.rating] += 1
        
        return {
            "product_id": product_id,
            "total_reviews": total_reviews,
            "average_rating": round(average_rating, 2),
            "rating_distribution": rating_distribution,
            "has_reviews": True
        }
        
    except Exception as e:
        print(f"Error in get_product_review_statistics: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/user/{user_id}/reviews", response_model=List[dict])
async def get_user_reviews(
    user_id: int,
    limit: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить отзывы пользователя
    """
    try:
        query = (
            select(ReviewModel)
            .where(ReviewModel.user_id == user_id)
            .order_by(desc(ReviewModel.created_at))
            .limit(limit)
        )
        
        result = await session.execute(query)
        reviews = result.scalars().all()
        
        return [review.to_dict() for review in reviews]
        
    except Exception as e:
        print(f"Error in get_user_reviews: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/health")
async def reviews_health_check(session: AsyncSession = Depends(get_async_session)):
    """
    Проверка работоспособности
    """
    try:
        result = await session.execute(select(func.count(ReviewModel.id)))
        count = result.scalar()
        
        return {
            "status": "healthy",
            "service": "reviews-api",
            "database": "connected",
            "total_reviews": count or 0,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "reviews-api",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
