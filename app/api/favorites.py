# app/api/favorites.py - минимальная рабочая версия
from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
import time

router = APIRouter(
    prefix="/favorites",
    tags=["Favorites"]
)


@router.get("/")
async def get_favorites():
    """Простой тестовый endpoint"""
    return {
        "message": "Favorites endpoint is working!",
        "timestamp": time.time()
    }


@router.get("/test")
async def test_endpoint():
    """Тестовый endpoint для проверки"""
    return {
        "status": "ok",
        "service": "favorites-api",
        "data": [
            {"id": 1, "user_id": 1, "product_id": 1},
            {"id": 2, "user_id": 1, "product_id": 2}
        ]
    }


@router.get("/user/{user_id}")
async def get_user_favorites(user_id: int):
    """Получить избранное пользователя (тестовые данные)"""
    return {
        "user_id": user_id,
        "favorites": [
            {"id": 1, "product_id": 1, "title": "Тестовый товар 1"},
            {"id": 2, "product_id": 2, "title": "Тестовый товар 2"}
        ]
    }


@router.post("/add")
async def add_favorite(favorite_data: dict):
    """Добавить в избранное (тестовые данные)"""
    return {
        "message": "Favorite added (test mode)",
        "data": favorite_data,
        "id": 999,
        "timestamp": time.time()
    }