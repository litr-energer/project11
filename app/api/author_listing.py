# app/api/author_listing.py
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_, or_, desc, asc
from datetime import datetime, timedelta
from decimal import Decimal
import json
import traceback

from app.database.database import get_async_session
from app.models.author_listing import AuthorListingModel
from app.models.users import UserModel

router = APIRouter(
    prefix="/author-listings",
    tags=["Author Listings"]
)


@router.get("/", response_model=List[dict])
async def get_author_listings(
    user_id: Optional[int] = Query(None, description="Фильтр по автору"),
    topics_games: Optional[str] = Query(None, description="Фильтр по теме игр"),
    category: Optional[str] = Query(None, description="Фильтр по категории"),
    status: Optional[str] = Query("active", description="Фильтр по статусу"),
    min_price: Optional[float] = Query(None, ge=0, description="Минимальная цена"),
    max_price: Optional[float] = Query(None, ge=0, description="Максимальная цена"),
    is_featured: Optional[bool] = Query(None, description="Только избранные"),
    search: Optional[str] = Query(None, description="Поиск по названию и описанию"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    order_by: str = Query("newest", description="Сортировка: newest, cheapest, expensive, popular, likes"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить список авторских объявлений
    """
    try:
        query = select(AuthorListingModel)
        
        if user_id:
            query = query.where(AuthorListingModel.user_id == user_id)
        
        if topics_games:
            query = query.where(AuthorListingModel.topics_games == topics_games)
        
        if category:
            query = query.where(AuthorListingModel.category == category)
        
        if status:
            query = query.where(AuthorListingModel.status == status)
        
        if min_price is not None:
            query = query.where(AuthorListingModel.price >= Decimal(str(min_price)))
        
        if max_price is not None:
            query = query.where(AuthorListingModel.price <= Decimal(str(max_price)))
        
        if is_featured is not None:
            query = query.where(AuthorListingModel.is_featured == is_featured)
        
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    AuthorListingModel.title.ilike(search_term),
                    AuthorListingModel.description.ilike(search_term)
                )
            )
        
        if order_by == "cheapest":
            query = query.order_by(asc(AuthorListingModel.price))
        elif order_by == "expensive":
            query = query.order_by(desc(AuthorListingModel.price))
        elif order_by == "popular":
            query = query.order_by(desc(AuthorListingModel.views_count))
        elif order_by == "likes":
            query = query.order_by(desc(AuthorListingModel.likes_count))
        else:  # "newest" по умолчанию
            query = query.order_by(desc(AuthorListingModel.created_at))
        
        query = query.offset(skip).limit(limit)
        
        result = await session.execute(query)
        listings = result.scalars().all()
        
        return [listing.to_dict() for listing in listings]
        
    except Exception as e:
        print(f"Error in get_author_listings: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{listing_id}", response_model=dict)
async def get_author_listing(
    listing_id: int,
    increment_views: bool = Query(True, description="Увеличить счетчик просмотров"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить авторское объявление по ID
    """
    try:
        query = select(AuthorListingModel).where(AuthorListingModel.id == listing_id)
        result = await session.execute(query)
        listing = result.scalar_one_or_none()
        
        if not listing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Author listing not found"
            )
        
        if listing.status != "active":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Author listing is not available"
            )
        
        if increment_views:
            listing.views_count += 1
            await session.commit()
            await session.refresh(listing)
        
        user_query = select(UserModel).where(UserModel.id == listing.user_id)
        user_result = await session.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        listing_dict = listing.to_dict()
        
        if user:
            listing_dict["author"] = {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        
        if listing_dict.get("image_urls"):
            try:
                listing_dict["image_urls_list"] = json.loads(listing_dict["image_urls"])
            except:
                listing_dict["image_urls_list"] = []
        
        return listing_dict
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_author_listing: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_author_listing(
    listing_data: dict,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Создать новое авторское объявление
    """
    try:
        required_fields = ['title', 'price', 'topics_games', 'user_id']
        for field in required_fields:
            if field not in listing_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required field: {field}"
                )
        
        user_query = select(UserModel).where(UserModel.id == listing_data['user_id'])
        user_result = await session.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        image_urls = listing_data.get('image_urls')
        if isinstance(image_urls, list):
            image_urls_json = json.dumps(image_urls)
        else:
            image_urls_json = image_urls
        
        listing = AuthorListingModel(
            title=listing_data['title'],
            description=listing_data.get('description'),
            price=Decimal(str(listing_data['price'])),
            topics_games=listing_data['topics_games'],
            category=listing_data.get('category'),
            image_url=listing_data.get('image_url'),
            image_urls=image_urls_json,
            user_id=listing_data['user_id'],
            file_url=listing_data.get('file_url'),
            file_size=listing_data.get('file_size'),
            status="active",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_featured=listing_data.get('is_featured', False)
        )
        
        session.add(listing)
        await session.commit()
        await session.refresh(listing)
        
        listing_dict = listing.to_dict()
        listing_dict["author"] = {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
        
        if listing_dict.get("image_urls"):
            try:
                listing_dict["image_urls_list"] = json.loads(listing_dict["image_urls"])
            except:
                listing_dict["image_urls_list"] = []
        
        return {
            **listing_dict,
            "message": "Author listing created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in create_author_listing: {e}")
        print(traceback.format_exc())
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.put("/{listing_id}", response_model=dict)
async def update_author_listing(
    listing_id: int,
    listing_data: dict,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Обновить авторское объявление
    """
    try:
        query = select(AuthorListingModel).where(AuthorListingModel.id == listing_id)
        result = await session.execute(query)
        listing = result.scalar_one_or_none()
        
        if not listing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Author listing not found"
            )
        
        if 'user_id' in listing_data and listing_data['user_id'] != listing.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own listings"
            )
        
        update_fields = [
            'title', 'description', 'price', 'topics_games', 
            'category', 'image_url', 'image_urls', 'status',
            'file_url', 'file_size', 'is_featured'
        ]
        
        for field in update_fields:
            if field in listing_data:
                if field == 'price':
                    setattr(listing, field, Decimal(str(listing_data[field])))
                elif field == 'image_urls' and isinstance(listing_data[field], list):
                    setattr(listing, field, json.dumps(listing_data[field]))
                else:
                    setattr(listing, field, listing_data[field])
        
        listing.updated_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(listing)
        
        listing_dict = listing.to_dict()
        
        if listing_dict.get("image_urls"):
            try:
                listing_dict["image_urls_list"] = json.loads(listing_dict["image_urls"])
            except:
                listing_dict["image_urls_list"] = []
        
        return {
            **listing_dict,
            "message": "Author listing updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in update_author_listing: {e}")
        print(traceback.format_exc())
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_author_listing(
    listing_id: int,
    user_id: int = Query(..., description="ID пользователя для проверки прав"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Удалить авторское объявление
    """
    try:
        query = select(AuthorListingModel).where(AuthorListingModel.id == listing_id)
        result = await session.execute(query)
        listing = result.scalar_one_or_none()
        
        if not listing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Author listing not found"
            )
        
        if listing.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own listings"
            )
        
        listing.status = "deleted"
        listing.updated_at = datetime.utcnow()
        
        await session.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in delete_author_listing: {e}")
        print(traceback.format_exc())
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/{listing_id}/like", response_model=dict)
async def like_author_listing(
    listing_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Поставить лайк авторскому объявлению
    """
    try:
        query = select(AuthorListingModel).where(AuthorListingModel.id == listing_id)
        result = await session.execute(query)
        listing = result.scalar_one_or_none()
        
        if not listing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Author listing not found"
            )
        
        listing.likes_count += 1
        listing.updated_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(listing)
        
        return {
            **listing.to_dict(),
            "message": "Listing liked successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in like_author_listing: {e}")
        print(traceback.format_exc())
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/{listing_id}/download", response_model=dict)
async def download_author_listing(
    listing_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Увеличить счетчик загрузок
    """
    try:
        query = select(AuthorListingModel).where(AuthorListingModel.id == listing_id)
        result = await session.execute(query)
        listing = result.scalar_one_or_none()
        
        if not listing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Author listing not found"
            )
        
        if not listing.file_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file available for download"
            )
        
        listing.downloads_count += 1
        listing.updated_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(listing)
        
        return {
            **listing.to_dict(),
            "message": "Download count updated",
            "file_url": listing.file_url,
            "file_size": listing.file_size
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in download_author_listing: {e}")
        print(traceback.format_exc())
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/author/{user_id}", response_model=List[dict])
async def get_author_listings_by_user(
    user_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить авторские объявления пользователя
    """
    try:
        user_query = select(UserModel).where(UserModel.id == user_id)
        user_result = await session.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        query = (
            select(AuthorListingModel)
            .where(AuthorListingModel.user_id == user_id)
            .where(AuthorListingModel.status == "active")
            .order_by(desc(AuthorListingModel.created_at))
        )
        
        result = await session.execute(query)
        listings = result.scalars().all()
        
        return [listing.to_dict() for listing in listings]
        
    except Exception as e:
        print(f"Error in get_author_listings_by_user: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/topics/available", response_model=List[str])
async def get_available_topics():
    """
    Получить список доступных тем игр
    """
    return [
        "Fantasy Art",
        "Sci-Fi Art", 
        "Game Music",
        "Sound Effects",
        "3D Models",
        "Game Mods",
        "Textures",
        "UI Elements",
        "Concept Art",
        "Character Designs",
        "Environment Art",
        "Game Assets",
        "Other"
    ]


@router.get("/categories/available", response_model=List[str])
async def get_available_categories():
    """
    Получить список доступных категорий
    """
    return [
        "artwork",
        "music", 
        "sound",
        "3d_model",
        "texture",
        "mod",
        "ui",
        "concept",
        "asset",
        "other"
    ]


@router.get("/featured", response_model=List[dict])
async def get_featured_author_listings(
    limit: int = Query(10, ge=1, le=50),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить избранные авторские объявления
    """
    try:
        query = (
            select(AuthorListingModel)
            .where(and_(
                AuthorListingModel.status == "active",
                AuthorListingModel.is_featured == True
            ))
            .order_by(desc(AuthorListingModel.likes_count))
            .limit(limit)
        )
        
        result = await session.execute(query)
        listings = result.scalars().all()
        
        return [listing.to_dict() for listing in listings]
        
    except Exception as e:
        print(f"Error in get_featured_author_listings: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/top/popular", response_model=List[dict])
async def get_popular_author_listings(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить популярные авторские объявления
    """
    try:
        query = (
            select(AuthorListingModel)
            .where(AuthorListingModel.status == "active")
            .order_by(desc(AuthorListingModel.likes_count))
            .limit(limit)
        )
        
        result = await session.execute(query)
        listings = result.scalars().all()
        
        return [listing.to_dict() for listing in listings]
        
    except Exception as e:
        print(f"Error in get_popular_author_listings: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/statistics", response_model=dict)
async def get_author_listings_statistics(
    user_id: Optional[int] = Query(None),
    days: int = Query(30, ge=1, le=365),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить статистику по авторским объявлениям
    """
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = select(AuthorListingModel).where(AuthorListingModel.created_at >= start_date)
        
        if user_id:
            query = query.where(AuthorListingModel.user_id == user_id)
        
        result = await session.execute(query)
        listings = result.scalars().all()
        
        total_listings = len(listings)
        active_listings = sum(1 for l in listings if l.status == "active")
        featured_listings = sum(1 for l in listings if l.is_featured)
        total_likes = sum(l.likes_count for l in listings)
        total_downloads = sum(l.downloads_count for l in listings)
        
        topics_stats = {}
        for listing in listings:
            topic = listing.topics_games
            topics_stats[topic] = topics_stats.get(topic, 0) + 1
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": datetime.utcnow().isoformat(),
                "days": days
            },
            "user_id": user_id,
            "statistics": {
                "total_listings": total_listings,
                "active_listings": active_listings,
                "featured_listings": featured_listings,
                "total_likes": total_likes,
                "total_downloads": total_downloads,
                "listings_by_topic": topics_stats
            }
        }
        
    except Exception as e:
        print(f"Error in get_author_listings_statistics: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/{listing_id}/feature", response_model=dict)
async def toggle_featured_author_listing(
    listing_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Переключить статус "избранное" для авторского объявления
    """
    try:
        query = select(AuthorListingModel).where(AuthorListingModel.id == listing_id)
        result = await session.execute(query)
        listing = result.scalar_one_or_none()
        
        if not listing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Author listing not found"
            )
        
        listing.is_featured = not listing.is_featured
        listing.updated_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(listing)
        
        return {
            **listing.to_dict(),
            "message": f"Listing {'marked as featured' if listing.is_featured else 'removed from featured'}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in toggle_featured_author_listing: {e}")
        print(traceback.format_exc())
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/health")
async def author_listings_health_check(session: AsyncSession = Depends(get_async_session)):
    """
    Проверка работоспособности
    """
    try:
        result = await session.execute(select(func.count(AuthorListingModel.id)))
        count = result.scalar()
        
        active_result = await session.execute(
            select(func.count(AuthorListingModel.id)).where(AuthorListingModel.status == "active")
        )
        active_count = active_result.scalar()
        
        return {
            "status": "healthy",
            "service": "author-listings-api",
            "database": "connected",
            "statistics": {
                "total_listings": count or 0,
                "active_listings": active_count or 0
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "author-listings-api",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }