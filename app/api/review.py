# app/api/review.py
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
    is_verified: Optional[bool] = Query(None, description="Только проверенные отзывы"),
    is_approved: Optional[bool] = Query(True, description="Только утвержденные отзывы"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    order_by: str = Query("newest", description="Сортировка: newest, oldest, highest_rating, lowest_rating, helpful"),
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
        
        if is_verified is not None:
            query = query.where(ReviewModel.is_verified == is_verified)
        
        if is_approved is not None:
            query = query.where(ReviewModel.is_approved == is_approved)
        
        # Сортировка
        if order_by == "oldest":
            query = query.order_by(asc(ReviewModel.created_at))
        elif order_by == "highest_rating":
            query = query.order_by(desc(ReviewModel.rating))
        elif order_by == "lowest_rating":
            query = query.order_by(asc(ReviewModel.rating))
        elif order_by == "helpful":
            query = query.order_by(desc(ReviewModel.helpful_count))
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
    
    Пример тела запроса:
    {
        "user_id": 1,
        "product_id": 5,
        "rating": 4,
        "title": "Отличный товар!",
        "comment": "Очень доволен покупкой",
        "listing_id": null,
        "author_listing_id": null
    }
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
                detail="At least one content ID must be specified (product_id, listing_id, or author_listing_id)"
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
        
        # Проверяем существование контента, если указан
        if 'product_id' in review_data and review_data['product_id']:
            product_query = select(ProductModel).where(ProductModel.id == review_data['product_id'])
            product_result = await session.execute(product_query)
            product = product_result.scalar_one_or_none()
            
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Product not found"
                )
        
        if 'listing_id' in review_data and review_data['listing_id']:
            listing_query = select(ListingModel).where(ListingModel.id == review_data['listing_id'])
            listing_result = await session.execute(listing_query)
            listing = listing_result.scalar_one_or_none()
            
            if not listing:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Listing not found"
                )
        
        if 'author_listing_id' in review_data and review_data['author_listing_id']:
            author_listing_query = select(AuthorListingModel).where(AuthorListingModel.id == review_data['author_listing_id'])
            author_listing_result = await session.execute(author_listing_query)
            author_listing = author_listing_result.scalar_one_or_none()
            
            if not author_listing:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Author listing not found"
                )
        
        # Проверяем, не оставлял ли пользователь уже отзыв на этот контент
        existing_conditions = [ReviewModel.user_id == review_data['user_id']]
        
        if 'product_id' in review_data and review_data['product_id']:
            existing_conditions.append(ReviewModel.product_id == review_data['product_id'])
        
        if 'listing_id' in review_data and review_data['listing_id']:
            existing_conditions.append(ReviewModel.listing_id == review_data['listing_id'])
        
        if 'author_listing_id' in review_data and review_data['author_listing_id']:
            existing_conditions.append(ReviewModel.author_listing_id == review_data['author_listing_id'])
        
        existing_query = select(ReviewModel).where(and_(*existing_conditions))
        existing_result = await session.execute(existing_query)
        existing_review = existing_result.scalar_one_or_none()
        
        if existing_review:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already reviewed this content"
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
            updated_at=datetime.utcnow(),
            is_verified=review_data.get('is_verified', False),
            is_approved=review_data.get('is_approved', True)
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


@router.put("/{review_id}", response_model=dict)
async def update_review(
    review_id: int,
    review_data: dict,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Обновить отзыв
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
        
        # Проверяем права пользователя
        if 'user_id' in review_data and review_data['user_id'] != review.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own reviews"
            )
        
        # Обновляем поля
        if 'rating' in review_data:
            new_rating = review_data['rating']
            if new_rating < 1 or new_rating > 5:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Rating must be between 1 and 5"
                )
            review.rating = new_rating
        
        if 'title' in review_data:
            review.title = review_data['title']
        
        if 'comment' in review_data:
            review.comment = review_data['comment']
        
        if 'is_verified' in review_data:
            review.is_verified = review_data['is_verified']
        
        if 'is_approved' in review_data:
            review.is_approved = review_data['is_approved']
        
        review.updated_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(review)
        
        return {
            **review.to_dict(),
            "message": "Review updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in update_review: {e}")
        print(traceback.format_exc())
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: int,
    user_id: int = Query(..., description="ID пользователя для проверки прав"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Удалить отзыв
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
        
        # Проверяем права пользователя
        if review.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own reviews"
            )
        
        await session.delete(review)
        await session.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in delete_review: {e}")
        print(traceback.format_exc())
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/{review_id}/helpful", response_model=dict)
async def mark_review_helpful(
    review_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Отметить отзыв как полезный
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
        
        review.helpful_count += 1
        review.updated_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(review)
        
        return {
            **review.to_dict(),
            "message": "Review marked as helpful"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in mark_review_helpful: {e}")
        print(traceback.format_exc())
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/product/{product_id}/statistics", response_model=dict)
async def get_product_review_statistics(
    product_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить статистику отзывов для товара
    """
    try:
        # Проверяем существование товара
        product_query = select(ProductModel).where(ProductModel.id == product_id)
        product_result = await session.execute(product_query)
        product = product_result.scalar_one_or_none()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Получаем все отзывы для товара
        reviews_query = select(ReviewModel).where(
            and_(
                ReviewModel.product_id == product_id,
                ReviewModel.is_approved == True
            )
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
        
        # Процентное распределение
        rating_percentages = {}
        for rating, count in rating_distribution.items():
            rating_percentages[rating] = round((count / total_reviews) * 100, 2)
        
        # Количество полезных отзывов
        helpful_reviews = sum(1 for review in reviews if review.helpful_count > 0)
        
        # Количество проверенных отзывов
        verified_reviews = sum(1 for review in reviews if review.is_verified)
        
        return {
            "product_id": product_id,
            "total_reviews": total_reviews,
            "average_rating": round(average_rating, 2),
            "rating_distribution": rating_distribution,
            "rating_percentages": rating_percentages,
            "helpful_reviews": helpful_reviews,
            "verified_reviews": verified_reviews,
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
        # Проверяем существование пользователя
        user_query = select(UserModel).where(UserModel.id == user_id)
        user_result = await session.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
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


@router.get("/content/{content_type}/{content_id}", response_model=List[dict])
async def get_content_reviews(
    content_type: str,  # product, listing, author_listing
    content_id: int,
    limit: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить отзывы для контента
    """
    try:
        query = select(ReviewModel).where(ReviewModel.is_approved == True)
        
        if content_type == "product":
            query = query.where(ReviewModel.product_id == content_id)
            # Проверяем существование товара
            content_query = select(ProductModel).where(ProductModel.id == content_id)
        elif content_type == "listing":
            query = query.where(ReviewModel.listing_id == content_id)
            content_query = select(ListingModel).where(ListingModel.id == content_id)
        elif content_type == "author_listing":
            query = query.where(ReviewModel.author_listing_id == content_id)
            content_query = select(AuthorListingModel).where(AuthorListingModel.id == content_id)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid content type. Use: product, listing, or author_listing"
            )
        
        # Проверяем существование контента
        content_result = await session.execute(content_query)
        content = content_result.scalar_one_or_none()
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{content_type.capitalize()} not found"
            )
        
        query = query.order_by(desc(ReviewModel.created_at)).limit(limit)
        
        result = await session.execute(query)
        reviews = result.scalars().all()
        
        return [review.to_dict() for review in reviews]
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_content_reviews: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/recent", response_model=List[dict])
async def get_recent_reviews(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить недавние отзывы
    """
    try:
        query = (
            select(ReviewModel)
            .where(ReviewModel.is_approved == True)
            .order_by(desc(ReviewModel.created_at))
            .limit(limit)
        )
        
        result = await session.execute(query)
        reviews = result.scalars().all()
        
        return [review.to_dict() for review in reviews]
        
    except Exception as e:
        print(f"Error in get_recent_reviews: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/admin/{review_id}/approve", response_model=dict)
async def approve_review(
    review_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Одобрить отзыв (админская функция)
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
        
        review.is_approved = True
        review.updated_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(review)
        
        return {
            **review.to_dict(),
            "message": "Review approved"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in approve_review: {e}")
        print(traceback.format_exc())
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/admin/{review_id}/verify", response_model=dict)
async def verify_review(
    review_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Проверить отзыв (отметить как проверенный)
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
        
        review.is_verified = True
        review.updated_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(review)
        
        return {
            **review.to_dict(),
            "message": "Review verified"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in verify_review: {e}")
        print(traceback.format_exc())
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/statistics", response_model=dict)
async def get_reviews_statistics(
    days: int = Query(30, ge=1, le=365),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить статистику по отзывам
    """
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = select(ReviewModel).where(ReviewModel.created_at >= start_date)
        result = await session.execute(query)
        reviews = result.scalars().all()
        
        total_reviews = len(reviews)
        approved_reviews = sum(1 for r in reviews if r.is_approved)
        verified_reviews = sum(1 for r in reviews if r.is_verified)
        
        if total_reviews > 0:
            average_rating = sum(r.rating for r in reviews) / total_reviews
            product_reviews = sum(1 for r in reviews if r.product_id)
            listing_reviews = sum(1 for r in reviews if r.listing_id)
            author_listing_reviews = sum(1 for r in reviews if r.author_listing_id)
        else:
            average_rating = 0
            product_reviews = 0
            listing_reviews = 0
            author_listing_reviews = 0
        
        # Распределение по дням
        reviews_by_day = {}
        for review in reviews:
            day = review.created_at.date().isoformat() if review.created_at else "unknown"
            reviews_by_day[day] = reviews_by_day.get(day, 0) + 1
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": datetime.utcnow().isoformat(),
                "days": days
            },
            "statistics": {
                "total_reviews": total_reviews,
                "approved_reviews": approved_reviews,
                "verified_reviews": verified_reviews,
                "average_rating": round(average_rating, 2),
                "by_content_type": {
                    "product": product_reviews,
                    "listing": listing_reviews,
                    "author_listing": author_listing_reviews
                },
                "reviews_by_day": reviews_by_day
            }
        }
        
    except Exception as e:
        print(f"Error in get_reviews_statistics: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/search", response_model=List[dict])
async def search_reviews(
    q: str = Query(..., min_length=2, description="Поисковый запрос"),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Поиск отзывов по тексту
    """
    try:
        search_term = f"%{q}%"
        
        query = (
            select(ReviewModel)
            .where(
                and_(
                    ReviewModel.is_approved == True,
                    or_(
                        ReviewModel.title.ilike(search_term),
                        ReviewModel.comment.ilike(search_term)
                    )
                )
            )
            .order_by(desc(ReviewModel.created_at))
            .limit(limit)
        )
        
        result = await session.execute(query)
        reviews = result.scalars().all()
        
        return [review.to_dict() for review in reviews]
        
    except Exception as e:
        print(f"Error in search_reviews: {e}")
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