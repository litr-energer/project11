# app/api/cart.py (исправленная версия)
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
import traceback

from app.database.database import get_async_session
from app.models.carts import CartModel
from app.models.cart_items import CartItemModel
from app.models.products import ProductModel

router = APIRouter(
    prefix="/cart",
    tags=["Cart"]
)


@router.get("/user/{user_id}", response_model=dict)
async def get_user_cart(
    user_id: int,
    with_items: bool = Query(True, description="Включить элементы корзины"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить корзину пользователя (или создать новую)
    """
    try:
        # Ищем существующую корзину пользователя
        cart_query = select(CartModel).where(CartModel.user_id == user_id)
        cart_result = await session.execute(cart_query)
        cart = cart_result.scalar_one_or_none()
        
        if not cart:
            # Создаем новую корзину
            cart = CartModel(
                user_id=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            session.add(cart)
            await session.commit()
            await session.refresh(cart)
        
        cart_dict = cart.to_dict()
        
        if with_items:
            # Получаем элементы корзины
            items_query = select(CartItemModel).where(CartItemModel.cart_id == cart.id)
            items_result = await session.execute(items_query)
            cart_items = items_result.scalars().all()
            
            # Получаем информацию о продуктах
            items_with_products = []
            for item in cart_items:
                if item.product_id:
                    product_query = select(ProductModel).where(ProductModel.id == item.product_id)
                    product_result = await session.execute(product_query)
                    product = product_result.scalar_one_or_none()
                    
                    if product:
                        items_with_products.append({
                            **item.to_dict(),
                            "product": {
                                "id": product.id,
                                "title": product.title,
                                "description": product.description,
                                "price": float(product.price) if product.price else None,
                                "category": product.category,
                                "image_url": product.image_url,
                                "is_active": product.is_active
                            },
                            "subtotal": float(product.price * item.quantity) if product.price else None
                        })
                    else:
                        items_with_products.append(item.to_dict())
                else:
                    items_with_products.append(item.to_dict())
            
            cart_dict["items"] = items_with_products
            
            # Подсчитываем итоги
            total_quantity = sum(item.quantity for item in cart_items)
            total_price = sum(
                float(product.price * item.quantity) 
                for item in cart_items 
                if item.product_id and product and product.price
                for product in [await session.execute(
                    select(ProductModel).where(ProductModel.id == item.product_id)
                ).scalar_one_or_none()]
                if product
            )
            
            cart_dict["summary"] = {
                "total_items": len(cart_items),
                "total_quantity": total_quantity,
                "total_price": round(total_price, 2) if total_price else 0
            }
        
        return cart_dict
        
    except Exception as e:
        print(f"Error in get_user_cart: {e}")
        print(traceback.format_exc())
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/user/{user_id}/create", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_cart(
    user_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Создать новую корзину для пользователя
    """
    try:
        # Проверяем, есть ли уже корзина у пользователя
        existing_cart_query = select(CartModel).where(CartModel.user_id == user_id)
        existing_cart_result = await session.execute(existing_cart_query)
        existing_cart = existing_cart_result.scalar_one_or_none()
        
        if existing_cart:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has a cart"
            )
        
        # Создаем новую корзину
        cart = CartModel(
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        session.add(cart)
        await session.commit()
        await session.refresh(cart)
        
        return {
            **cart.to_dict(),
            "message": "Cart created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in create_cart: {e}")
        print(traceback.format_exc())
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/{cart_id}/items", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_item_to_cart(
    cart_id: int,
    item_data: dict,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Добавить товар в корзину
    """
    try:
        # Проверяем существование корзины
        cart_query = select(CartModel).where(CartModel.id == cart_id)
        cart_result = await session.execute(cart_query)
        cart = cart_result.scalar_one_or_none()
        
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart not found"
            )
        
        # Проверяем данные
        product_id = item_data.get('product_id')
        listing_id = item_data.get('listing_id')
        author_listing_id = item_data.get('author_listing_id')
        quantity = item_data.get('quantity', 1)
        
        if not any([product_id, listing_id, author_listing_id]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one content ID must be specified"
            )
        
        # Проверяем товар, если указан
        if product_id:
            product_query = select(ProductModel).where(ProductModel.id == product_id)
            product_result = await session.execute(product_query)
            product = product_result.scalar_one_or_none()
            
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Product not found"
                )
            
            if not product.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Product is not available"
                )
        
        # Проверяем, есть ли уже такой товар в корзине
        existing_item_query = select(CartItemModel).where(
            and_(
                CartItemModel.cart_id == cart_id,
                CartItemModel.product_id == product_id,
                CartItemModel.listing_id == listing_id,
                CartItemModel.author_listing_id == author_listing_id
            )
        )
        existing_item_result = await session.execute(existing_item_query)
        existing_item = existing_item_result.scalar_one_or_none()
        
        if existing_item:
            # Обновляем количество
            existing_item.quantity += quantity
            existing_item.added_at = datetime.utcnow()
        else:
            # Создаем новый элемент
            cart_item = CartItemModel(
                cart_id=cart_id,
                product_id=product_id,
                listing_id=listing_id,
                author_listing_id=author_listing_id,
                quantity=quantity,
                added_at=datetime.utcnow()
            )
            session.add(cart_item)
        
        # Обновляем время корзины
        cart.updated_at = datetime.utcnow()
        
        await session.commit()
        
        if existing_item:
            await session.refresh(existing_item)
            return {
                **existing_item.to_dict(),
                "message": "Quantity updated in cart",
                "action": "updated"
            }
        else:
            # Получаем ID нового элемента
            await session.refresh(cart_item)
            return {
                **cart_item.to_dict(),
                "message": "Item added to cart",
                "action": "added"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in add_item_to_cart: {e}")
        print(traceback.format_exc())
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{cart_id}/summary", response_model=dict)
async def get_cart_summary(
    cart_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить сводку по корзине
    """
    try:
        cart_query = select(CartModel).where(CartModel.id == cart_id)
        cart_result = await session.execute(cart_query)
        cart = cart_result.scalar_one_or_none()
        
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart not found"
            )
        
        # Получаем элементы корзины
        items_query = select(CartItemModel).where(CartItemModel.cart_id == cart_id)
        items_result = await session.execute(items_query)
        cart_items = items_result.scalars().all()
        
        total_quantity = 0
        total_price = 0.0
        items_summary = []
        
        for item in cart_items:
            if item.product_id:
                product_query = select(ProductModel).where(ProductModel.id == item.product_id)
                product_result = await session.execute(product_query)
                product = product_result.scalar_one_or_none()
                
                if product and product.price:
                    subtotal = float(product.price) * item.quantity
                    total_price += subtotal
                    total_quantity += item.quantity
                    
                    items_summary.append({
                        "id": item.id,
                        "product_id": product.id,
                        "title": product.title,
                        "quantity": item.quantity,
                        "price": float(product.price),
                        "subtotal": round(subtotal, 2),
                        "image_url": product.image_url,
                        "is_available": product.is_active
                    })
        
        return {
            "cart_id": cart_id,
            "user_id": cart.user_id,
            "summary": {
                "total_items": len(cart_items),
                "total_quantity": total_quantity,
                "total_price": round(total_price, 2),
                "items": items_summary,
                "last_updated": cart.updated_at.isoformat() if cart.updated_at else None
            }
        }
        
    except Exception as e:
        print(f"Error in get_cart_summary: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/{cart_id}/clear", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    cart_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Очистить корзину (удалить все элементы)
    """
    try:
        cart_query = select(CartModel).where(CartModel.id == cart_id)
        cart_result = await session.execute(cart_query)
        cart = cart_result.scalar_one_or_none()
        
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart not found"
            )
        
        # Удаляем все элементы корзины
        items_query = select(CartItemModel).where(CartItemModel.cart_id == cart_id)
        items_result = await session.execute(items_query)
        items = items_result.scalars().all()
        
        for item in items:
            await session.delete(item)
        
        cart.updated_at = datetime.utcnow()
        await session.commit()
        
    except Exception as e:
        print(f"Error in clear_cart: {e}")
        print(traceback.format_exc())
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/health")
async def cart_health_check(session: AsyncSession = Depends(get_async_session)):
    """
    Проверка работоспособности
    """
    try:
        carts_count_query = select(func.count(CartModel.id))
        carts_count_result = await session.execute(carts_count_query)
        carts_count = carts_count_result.scalar()
        
        items_count_query = select(func.count(CartItemModel.id))
        items_count_result = await session.execute(items_count_query)
        items_count = items_count_result.scalar()
        
        return {
            "status": "healthy",
            "service": "cart-api",
            "database": "connected",
            "statistics": {
                "total_carts": carts_count or 0,
                "total_cart_items": items_count or 0
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "cart-api",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }