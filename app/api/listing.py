# app/api/listing.py
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_, or_, desc, asc
from datetime import datetime, timedelta
from decimal import Decimal
import json
import traceback

from app.database.database import get_async_session
from app.models.listing import ListingModel
from app.models.users import UserModel  # Предполагаем наличие модели пользователя

router = APIRouter(
    prefix="/listings",
    tags=["Listings"]
)


@router.get("/", response_model=List[dict])
async def get_listings(
    user_id: Optional[int] = Query(None, description="Фильтр по пользователю"),
    game_topic: Optional[str] = Query(None, description="Фильтр по теме игры"),
    game_platform: Optional[str] = Query(None, description="Фильтр по платформе"),
    game_region: Optional[str] = Query(None, description="Фильтр по региону"),
    status: Optional[str] = Query("active", description="Фильтр по статусу"),
    min_price: Optional[float] = Query(None, ge=0, description="Минимальная цена"),
    max_price: Optional[float] = Query(None, ge=0, description="Максимальная цена"),
    is_featured: Optional[bool] = Query(None, description="Только избранные"),
    search: Optional[str] = Query(None, description="Поиск по названию и описанию"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    order_by: str = Query("newest", description="Сортировка: newest, cheapest, expensive, popular"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить список объявлений с фильтрацией и пагинацией
    """
    try:
        query = select(ListingModel)
        
        # Применяем фильтры
        if user_id:
            query = query.where(ListingModel.user_id == user_id)
        
        if game_topic:
            query = query.where(ListingModel.game_topic == game_topic)
        
        if game_platform:
            query = query.where(ListingModel.game_platform == game_platform)
        
        if game_region:
            query = query.where(ListingModel.game_region == game_region)
        
        if status:
            query = query.where(ListingModel.status == status)
        
        if min_price is not None:
            query = query.where(ListingModel.price >= Decimal(str(min_price)))
        
        if max_price is not None:
            query = query.where(ListingModel.price <= Decimal(str(max_price)))
        
        if is_featured is not None:
            query = query.where(ListingModel.is_featured == is_featured)
        
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    ListingModel.title.ilike(search_term),
                    ListingModel.description.ilike(search_term)
                )
            )
        
        # Сортировка
        if order_by == "cheapest":
            query = query.order_by(asc(ListingModel.price))
        elif order_by == "expensive":
            query = query.order_by(desc(ListingModel.price))
        elif order_by == "popular":
            query = query.order_by(desc(ListingModel.views_count))
        else:  # "newest" по умолчанию
            query = query.order_by(desc(ListingModel.created_at))
        
        # Пагинация
        query = query.offset(skip).limit(limit)
        
        result = await session.execute(query)
        listings = result.scalars().all()
        
        return [listing.to_dict() for listing in listings]
        
    except Exception as e:
        print(f"Error in get_listings: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{listing_id}", response_model=dict)
async def get_listing(
    listing_id: int,
    increment_views: bool = Query(True, description="Увеличить счетчик просмотров"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить объявление по ID
    """
    try:
        query = select(ListingModel).where(ListingModel.id == listing_id)
        result = await session.execute(query)
        listing = result.scalar_one_or_none()
        
        if not listing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Listing not found"
            )
        
        if listing.status != "active":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Listing is not available"
            )
        
        # Увеличиваем счетчик просмотров
        if increment_views:
            listing.views_count += 1
            await session.commit()
            await session.refresh(listing)
        
        # Получаем информацию о пользователе
        user_query = select(UserModel).where(UserModel.id == listing.user_id)
        user_result = await session.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        listing_dict = listing.to_dict()
        
        if user:
            listing_dict["user"] = {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        
        # Парсим image_urls если это JSON
        if listing_dict.get("image_urls"):
            try:
                listing_dict["image_urls_list"] = json.loads(listing_dict["image_urls"])
            except:
                listing_dict["image_urls_list"] = []
        
        return listing_dict
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_listing: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_listing(
    listing_data: dict,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Создать новое объявление
    
    Пример тела запроса:
    {
        "title": "Продаю аккаунт в игре",
        "description": "Полный доступ, много предметов",
        "price": 2999.99,
        "game_topic": "World of Warcraft",
        "game_platform": "PC",
        "game_region": "EU",
        "image_url": "https://example.com/image.jpg",
        "image_urls": ["url1", "url2"],
        "user_id": 1
    }
    """
    try:
        # Проверяем обязательные поля
        required_fields = ['title', 'price', 'game_topic', 'user_id']
        for field in required_fields:
            if field not in listing_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required field: {field}"
                )
        
        # Проверяем существование пользователя
        user_query = select(UserModel).where(UserModel.id == listing_data['user_id'])
        user_result = await session.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Обрабатываем image_urls если это список
        image_urls = listing_data.get('image_urls')
        if isinstance(image_urls, list):
            image_urls_json = json.dumps(image_urls)
        else:
            image_urls_json = image_urls
        
        # Создаем объявление
        listing = ListingModel(
            title=listing_data['title'],
            description=listing_data.get('description'),
            price=Decimal(str(listing_data['price'])),
            game_topic=listing_data['game_topic'],
            game_platform=listing_data.get('game_platform'),
            game_region=listing_data.get('game_region'),
            image_url=listing_data.get('image_url'),
            image_urls=image_urls_json,
            user_id=listing_data['user_id'],
            status="active",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            views_count=0,
            is_featured=listing_data.get('is_featured', False)
        )
        
        session.add(listing)
        await session.commit()
        await session.refresh(listing)
        
        listing_dict = listing.to_dict()
        
        # Добавляем информацию о пользователе
        listing_dict["user"] = {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
        
        # Парсим image_urls если это JSON
        if listing_dict.get("image_urls"):
            try:
                listing_dict["image_urls_list"] = json.loads(listing_dict["image_urls"])
            except:
                listing_dict["image_urls_list"] = []
        
        return {
            **listing_dict,
            "message": "Listing created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in create_listing: {e}")
        print(traceback.format_exc())
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.put("/{listing_id}", response_model=dict)
async def update_listing(
    listing_id: int,
    listing_data: dict,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Обновить объявление
    """
    try:
        query = select(ListingModel).where(ListingModel.id == listing_id)
        result = await session.execute(query)
        listing = result.scalar_one_or_none()
        
        if not listing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Listing not found"
            )
        
        # Проверяем права пользователя (здесь простая проверка, можно добавить больше логики)
        if 'user_id' in listing_data and listing_data['user_id'] != listing.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own listings"
            )
        
        # Обновляем поля
        update_fields = [
            'title', 'description', 'price', 'game_topic', 
            'game_platform', 'game_region', 'image_url', 
            'image_urls', 'status', 'is_featured'
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
        
        # Парсим image_urls если это JSON
        if listing_dict.get("image_urls"):
            try:
                listing_dict["image_urls_list"] = json.loads(listing_dict["image_urls"])
            except:
                listing_dict["image_urls_list"] = []
        
        return {
            **listing_dict,
            "message": "Listing updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in update_listing: {e}")
        print(traceback.format_exc())
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_listing(
    listing_id: int,
    user_id: int = Query(..., description="ID пользователя для проверки прав"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Удалить объявление
    """
    try:
        query = select(ListingModel).where(ListingModel.id == listing_id)
        result = await session.execute(query)
        listing = result.scalar_one_or_none()
        
        if not listing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Listing not found"
            )
        
        # Проверяем права пользователя
        if listing.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own listings"
            )
        
        # Мягкое удаление - меняем статус
        listing.status = "deleted"
        listing.updated_at = datetime.utcnow()
        
        await session.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in delete_listing: {e}")
        print(traceback.format_exc())
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=List[dict])
async def get_user_listings(
    user_id: int,
    status: Optional[str] = Query("active", description="Фильтр по статусу"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить объявления пользователя
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
            select(ListingModel)
            .where(ListingModel.user_id == user_id)
            .where(ListingModel.status == status)
            .order_by(desc(ListingModel.created_at))
        )
        
        result = await session.execute(query)
        listings = result.scalars().all()
        
        return [listing.to_dict() for listing in listings]
        
    except Exception as e:
        print(f"Error in get_user_listings: {e}")
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
        "World of Warcraft",
        "Dota 2",
        "Counter-Strike",
        "League of Legends",
        "Valorant",
        "Minecraft",
        "Fortnite",
        "Apex Legends",
        "Call of Duty",
        "Escape from Tarkov",
        "Genshin Impact",
        "Diablo",
        "Path of Exile",
        "Other"
    ]


@router.get("/platforms/available", response_model=List[str])
async def get_available_platforms():
    """
    Получить список доступных платформ
    """
    return ["PC", "PlayStation", "Xbox", "Nintendo", "Mobile", "Cross-platform"]


@router.get("/regions/available", response_model=List[str])
async def get_available_regions():
    """
    Получить список доступных регионов
    """
    return ["RU", "EU", "NA", "ASIA", "Other"]


@router.get("/statuses/available", response_model=List[str])
async def get_available_statuses():
    """
    Получить список доступных статусов
    """
    return ["active", "pending", "sold", "reserved", "deleted"]


@router.post("/{listing_id}/feature", response_model=dict)
async def toggle_featured(
    listing_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Переключить статус "избранное" для объявления
    """
    try:
        query = select(ListingModel).where(ListingModel.id == listing_id)
        result = await session.execute(query)
        listing = result.scalar_one_or_none()
        
        if not listing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Listing not found"
            )
        
        # Переключаем статус
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
        print(f"Error in toggle_featured: {e}")
        print(traceback.format_exc())
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/search/suggestions", response_model=List[str])
async def get_search_suggestions(
    q: str = Query(..., min_length=2, description="Поисковый запрос"),
    limit: int = Query(10, ge=1, le=20),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить поисковые подсказки
    """
    try:
        search_term = f"%{q}%"
        
        query = (
            select(ListingModel.title)
            .where(
                and_(
                    ListingModel.status == "active",
                    or_(
                        ListingModel.title.ilike(search_term),
                        ListingModel.game_topic.ilike(search_term)
                    )
                )
            )
            .distinct()
            .limit(limit)
        )
        
        result = await session.execute(query)
        suggestions = result.scalars().all()
        
        return suggestions
        
    except Exception as e:
        print(f"Error in get_search_suggestions: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/statistics", response_model=dict)
async def get_listings_statistics(
    user_id: Optional[int] = Query(None, description="Статистика для конкретного пользователя"),
    days: int = Query(30, ge=1, le=365, description="За последние N дней"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить статистику по объявлениям
    """
    try:
        from sqlalchemy import func
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Базовый запрос
        query = select(ListingModel).where(ListingModel.created_at >= start_date)
        
        if user_id:
            query = query.where(ListingModel.user_id == user_id)
        
        result = await session.execute(query)
        listings = result.scalars().all()
        
        # Статистика
        total_listings = len(listings)
        active_listings = sum(1 for l in listings if l.status == "active")
        featured_listings = sum(1 for l in listings if l.is_featured)
        
        # Статистика по темам
        topics_stats = {}
        for listing in listings:
            topic = listing.game_topic
            topics_stats[topic] = topics_stats.get(topic, 0) + 1
        
        # Статистика по дням
        listings_by_day = {}
        for listing in listings:
            day = listing.created_at.date().isoformat() if listing.created_at else "unknown"
            listings_by_day[day] = listings_by_day.get(day, 0) + 1
        
        # Общее количество просмотров
        total_views = sum(listing.views_count for listing in listings)
        
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
                "total_views": total_views,
                "listings_by_topic": topics_stats,
                "listings_by_day": listings_by_day
            }
        }
        
    except Exception as e:
        print(f"Error in get_listings_statistics: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/featured", response_model=List[dict])
async def get_featured_listings(
    limit: int = Query(10, ge=1, le=50),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить избранные объявления
    """
    try:
        query = (
            select(ListingModel)
            .where(and_(
                ListingModel.status == "active",
                ListingModel.is_featured == True
            ))
            .order_by(desc(ListingModel.views_count))
            .limit(limit)
        )
        
        result = await session.execute(query)
        listings = result.scalars().all()
        
        return [listing.to_dict() for listing in listings]
        
    except Exception as e:
        print(f"Error in get_featured_listings: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/recent", response_model=List[dict])
async def get_recent_listings(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить недавние объявления
    """
    try:
        query = (
            select(ListingModel)
            .where(ListingModel.status == "active")
            .order_by(desc(ListingModel.created_at))
            .limit(limit)
        )
        
        result = await session.execute(query)
        listings = result.scalars().all()
        
        return [listing.to_dict() for listing in listings]
        
    except Exception as e:
        print(f"Error in get_recent_listings: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/health")
async def listings_health_check(session: AsyncSession = Depends(get_async_session)):
    """
    Проверка работоспособности
    """
    try:
        result = await session.execute(select(func.count(ListingModel.id)))
        count = result.scalar()
        
        active_result = await session.execute(
            select(func.count(ListingModel.id)).where(ListingModel.status == "active")
        )
        active_count = active_result.scalar()
        
        return {
            "status": "healthy",
            "service": "listings-api",
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
            "service": "listings-api",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
