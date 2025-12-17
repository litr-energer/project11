from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.cart_schema import Cart, CartItem, CartItemCreate, CartItemUpdate
from app.services.cart_service import CartService
from app.repositories.cart_repository import CartRepository
from app.repositories.cart_item_repository import CartItemRepository
from app.models.products import ProductModel
from app.models.listing import ListingModel
from app.models.author_listing import AuthorListingModel

router = APIRouter(prefix="/carts", tags=["carts"])

def get_cart_service(db: Session = Depends(get_db)) -> CartService:
    cart_repository = CartRepository(db)
    cart_item_repository = CartItemRepository(db)
    return CartService(cart_repository, cart_item_repository)

# Получаем корзину текущего пользователя (из сессии или JWT токена)
async def get_current_user_id(request: Request):
    # В реальном приложении здесь должна быть аутентификация
    # Например, через JWT токен или сессию
    # Пока используем заглушку
    user_id = request.headers.get("X-User-Id")
    if not user_id:
        # Для демо - используем 1, но в реальности нужно требовать авторизацию
        raise HTTPException(status_code=401, detail="User not authenticated")
    return int(user_id)

@router.get("/my", response_model=Cart)
async def get_my_cart(
    request: Request,
    cart_service: CartService = Depends(get_cart_service)
):
    """Получить корзину текущего пользователя"""
    user_id = await get_current_user_id(request)
    return cart_service.get_or_create_user_cart(user_id)

@router.get("/my/items", response_model=List[CartItem])
async def get_my_cart_items(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    cart_service: CartService = Depends(get_cart_service)
):
    """Получить элементы корзины текущего пользователя"""
    user_id = await get_current_user_id(request)
    cart = cart_service.get_or_create_user_cart(user_id)
    return cart_service.get_cart_items(cart.id, skip, limit)

@router.get("/my/items/detailed")
async def get_my_cart_items_detailed(
    request: Request,
    db: Session = Depends(get_db),
    cart_service: CartService = Depends(get_cart_service)
):
    """Получить элементы корзины с полными данными о товарах"""
    user_id = await get_current_user_id(request)
    cart = cart_service.get_or_create_user_cart(user_id)
    
    items = cart_service.get_cart_items(cart.id)
    
    # Обогащаем данные информацией о товарах
    detailed_items = []
    for item in items:
        item_data = {
            "id": item.id,
            "cart_id": item.cart_id,
            "item_type": item.item_type,
            "product_id": item.product_id,
            "listing_id": item.listing_id,
            "author_listing_id": item.author_listing_id,
            "quantity": item.quantity,
            "price": float(item.price),
            "created_at": item.created_at.isoformat() if item.created_at else None,
            "title": "Unknown Item",
            "description": "",
            "image_url": "https://via.placeholder.com/120x90?text=No+Image",
            "category": ""
        }
        
        # Загружаем полные данные товара в зависимости от типа
        if item.item_type == 'product' and item.product_id:
            product = db.query(ProductModel).filter(ProductModel.id == item.product_id).first()
            if product:
                item_data["title"] = product.title
                item_data["description"] = product.description or ""
                item_data["image_url"] = product.image_url or "https://via.placeholder.com/120x90?text=Product"
                item_data["category"] = product.category
        
        elif item.item_type == 'listing' and item.listing_id:
            listing = db.query(ListingModel).filter(ListingModel.id == item.listing_id).first()
            if listing:
                item_data["title"] = listing.title
                item_data["description"] = listing.game_topic
                item_data["image_url"] = listing.image_url or "https://via.placeholder.com/120x90?text=Listing"
                item_data["category"] = "Listing"
        
        elif item.item_type == 'author_listing' and item.author_listing_id:
            author_listing = db.query(AuthorListingModel).filter(AuthorListingModel.id == item.author_listing_id).first()
            if author_listing:
                item_data["title"] = author_listing.title
                item_data["description"] = ""
                item_data["image_url"] = author_listing.image_url or "https://via.placeholder.com/120x90?text=Author+Listing"
                item_data["category"] = "Author Publication"
        
        detailed_items.append(item_data)
    
    return detailed_items

@router.post("/my/items", response_model=CartItem)
async def add_item_to_my_cart(
    request: Request,
    item_data: CartItemCreate,
    cart_service: CartService = Depends(get_cart_service)
):
    """Добавить товар в корзину текущего пользователя"""
    user_id = await get_current_user_id(request)
    cart = cart_service.get_or_create_user_cart(user_id)
    
    # Логируем полученные данные для отладки
    print("=== ДАННЫЕ ОТ ФРОНТЕНДА ===")
    print(f"item_type: {item_data.item_type}")
    print(f"product_id: {item_data.product_id}")
    print(f"listing_id: {item_data.listing_id}")
    print(f"author_listing_id: {item_data.author_listing_id}")
    print(f"quantity: {item_data.quantity}")
    print(f"price: {item_data.price}")
    print("===========================")
    
    # Ручная проверка (заменяем валидаторы Pydantic)
    if item_data.item_type == 'product':
        if not item_data.product_id:
            raise HTTPException(
                status_code=422, 
                detail="Для товара требуется product_id"
            )
        item_id = item_data.product_id
        id_field = 'product_id'
    elif item_data.item_type == 'listing':
        if not item_data.listing_id:
            raise HTTPException(
                status_code=422, 
                detail="Для публикации требуется listing_id"
            )
        item_id = item_data.listing_id
        id_field = 'listing_id'
    elif item_data.item_type == 'author_listing':
        if not item_data.author_listing_id:
            raise HTTPException(
                status_code=422, 
                detail="Для авторского издания требуется author_listing_id"
            )
        item_id = item_data.author_listing_id
        id_field = 'author_listing_id'
    else:
        raise HTTPException(status_code=422, detail="Неизвестный тип товара")
    
    # Подготавливаем данные для сервиса
    item_dict = {
        'cart_id': cart.id,
        'item_type': item_data.item_type.value if hasattr(item_data.item_type, 'value') else item_data.item_type,
        id_field: item_id,
        'item_id': item_id,
        'quantity': item_data.quantity,
        'price': item_data.price
    }
    
    print("=== ДАННЫЕ ДЛЯ СЕРВИСА ===")
    print(item_dict)
    print("===========================")
    
    # Передаем в сервис
    return cart_service.add_item_to_cart(cart.id, item_dict)

@router.put("/my/items/{item_id}", response_model=CartItem)
async def update_my_cart_item(
    request: Request,
    item_id: int,
    item_data: CartItemUpdate,
    cart_service: CartService = Depends(get_cart_service)
):
    """Обновить товар в корзине текущего пользователя"""
    user_id = await get_current_user_id(request)
    cart = cart_service.get_or_create_user_cart(user_id)
    
    # Проверяем, что товар принадлежит корзине пользователя
    item = cart_service.cart_item_repository.get(item_id)
    if not item or item.cart_id != cart.id:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    return cart_service.update_cart_item_quantity(item_id, item_data.quantity or 1)

@router.delete("/my/items/{item_id}")
async def remove_item_from_my_cart(
    request: Request,
    item_id: int,
    cart_service: CartService = Depends(get_cart_service)
):
    """Удалить товар из корзины текущего пользователя"""
    user_id = await get_current_user_id(request)
    cart = cart_service.get_or_create_user_cart(user_id)
    
    # Проверяем, что товар принадлежит корзине пользователя
    item = cart_service.cart_item_repository.get(item_id)
    if not item or item.cart_id != cart.id:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    success = cart_service.remove_item_from_cart(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return {"message": "Item removed from cart"}

@router.delete("/my/clear")
async def clear_my_cart(
    request: Request,
    cart_service: CartService = Depends(get_cart_service)
):
    """Очистить корзину текущего пользователя"""
    user_id = await get_current_user_id(request)
    cart = cart_service.get_or_create_user_cart(user_id)
    
    cart_service.clear_cart(cart.id)
    return {"message": "Cart cleared successfully"}

@router.get("/my/total")
async def get_my_cart_total(
    request: Request,
    cart_service: CartService = Depends(get_cart_service)
):
    """Получить общую стоимость корзины"""
    user_id = await get_current_user_id(request)
    cart = cart_service.get_or_create_user_cart(user_id)
    
    total = cart_service.get_cart_total(cart.id)
    return {"total": total}
