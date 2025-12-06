# app/api/cart.py
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status, Query, Depends, Header, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
import uuid
import traceback

from app.database.database import get_async_session
from app.models.cart_items import CartItemModel
from app.models.products import ProductModel

router = APIRouter(
    prefix="/cart",
    tags=["Cart"]
)


def get_cart_session_id(
    cart_session_id: Optional[str] = Cookie(None, alias="cart_session_id"),
    x_cart_session_id: Optional[str] = Header(None, alias="X-Cart-Session-Id")
) -> str:
    """
    Получить или создать ID сессии корзины
    """
    if cart_session_id:
        return cart_session_id
    elif x_cart_session_id:
        return x_cart_session_id
    else:
        # Генерируем новый ID сессии
        return str(uuid.uuid4())


@router.get("/items", response_model=List[dict])
async def get_cart_items(
    user_id: Optional[int] = Query(None, description="ID пользователя"),
    cart_session_id: Optional[str] = Query(None, description="ID сессии корзины"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить элементы корзины
    """
    try:
        query = select(CartItemModel)
        
        if user_id:
            query = query.where(CartItemModel.user_id == user_id)
        elif cart_session_id:
            # Для неавторизованных пользователей
            query = query.where(CartItemModel.cart_session_id == cart_session_id)
        else:
            return []
        
        query = query.order_by(CartItemModel.added_at.desc())
        
        result = await session.execute(query)
        cart_items = result.scalars().all()
        
        return [item.to_dict() for item in cart_items]
        
    except Exception as e:
        print(f"Error in get_cart_items: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/user/{user_id}/items", response_model=List[dict])
async def get_user_cart_items(
    user_id: int,
    with_products: bool = Query(False, description="Включить информацию о продуктах"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить элементы корзины пользователя
    """
    try:
        if with_products:
            # Получаем элементы корзины с информацией о продуктах
            query = (
                select(CartItemModel, ProductModel)
                .join(ProductModel, CartItemModel.product_id == ProductModel.id)
                .where(CartItemModel.user_id == user_id)
                .where(CartItemModel.product_id.isnot(None))
                .order_by(CartItemModel.added_at.desc())
            )
            
            result = await session.execute(query)
            items_with_products = result.all()
            
            return [
                {
                    **item.to_dict(),
                    "product": {
                        "id": product.id,
                        "title": product.title,
                        "description": product.description,
                        "price": float(product.price) if product.price else None,
                        "category": product.category,
                        "image_url": product.image_url
                    },
                    "subtotal": float(product.price * item.quantity) if product.price else None
                }
                for item, product in items_with_products
            ]
        else:
            # Только элементы корзины
            query = (
                select(CartItemModel)
                .where(CartItemModel.user_id == user_id)
                .order_by(CartItemModel.added_at.desc())
            )
            
            result = await session.execute(query)
            cart_items = result.scalars().all()
            
            return [item.to_dict() for item in cart_items]
        
    except Exception as e:
        print(f"Error in get_user_cart_items: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/items", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    cart_data: dict,
    cart_session_id: str = Depends(get_cart_session_id),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Добавить товар в корзину
    
    Пример тела запроса:
    {
        "user_id": 1,  # Опционально для авторизованных пользователей
        "product_id": 5,
        "listing_id": null,
        "author_listing_id": null,
        "quantity": 2
    }
    """
    try:
        # Проверяем обязательные поля
        if not any([cart_data.get('product_id'), cart_data.get('listing_id'), cart_data.get('author_listing_id')]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one content ID must be specified (product_id, listing_id, or author_listing_id)"
            )
        
        user_id = cart_data.get('user_id')
        product_id = cart_data.get('product_id')
        listing_id = cart_data.get('listing_id')
        author_listing_id = cart_data.get('author_listing_id')
        quantity = cart_data.get('quantity', 1)
        
        # Проверяем наличие товара, если указан product_id
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
        query_conditions = []
        if user_id:
            query_conditions.append(CartItemModel.user_id == user_id)
        else:
            query_conditions.append(CartItemModel.cart_session_id == cart_session_id)
        
        if product_id:
            query_conditions.append(CartItemModel.product_id == product_id)
        if listing_id:
            query_conditions.append(CartItemModel.listing_id == listing_id)
        if author_listing_id:
            query_conditions.append(CartItemModel.author_listing_id == author_listing_id)
        
        existing_query = select(CartItemModel).where(and_(*query_conditions))
        existing_result = await session.execute(existing_query)
        existing_item = existing_result.scalar_one_or_none()
        
        if existing_item:
            # Обновляем количество
            existing_item.quantity += quantity
            existing_item.added_at = datetime.utcnow()
            await session.commit()
            await session.refresh(existing_item)
            
            return {
                **existing_item.to_dict(),
                "message": "Quantity updated in cart",
                "action": "updated"
            }
        else:
            # Создаем новый элемент корзины
            db_cart_item = CartItemModel(
                user_id=user_id,
                cart_session_id=cart_session_id if not user_id else None,
                product_id=product_id,
                listing_id=listing_id,
                author_listing_id=author_listing_id,
                quantity=quantity,
                added_at=datetime.utcnow()
            )
            
            session.add(db_cart_item)
            await session.commit()
            await session.refresh(db_cart_item)
            
            response_data = {
                **db_cart_item.to_dict(),
                "message": "Item added to cart",
                "action": "added"
            }
            
            # Добавляем session_id в заголовки для клиента
            from fastapi import Response
            response = Response()
            response.set_cookie(
                key="cart_session_id",
                value=cart_session_id,
                max_age=30*24*60*60,  # 30 дней
                httponly=True,
                samesite="lax"
            )
            
            return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in add_to_cart: {e}")
        print(traceback.format_exc())
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.put("/items/{item_id}", response_model=dict)
async def update_cart_item(
    item_id: int,
    cart_data: dict,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Обновить элемент корзины (изменить количество)
    """
    try:
        query = select(CartItemModel).where(CartItemModel.id == item_id)
        result = await session.execute(query)
        cart_item = result.scalar_one_or_none()
        
        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found"
            )
        
        # Обновляем количество
        if 'quantity' in cart_data:
            new_quantity = cart_data['quantity']
            if new_quantity <= 0:
                # Если количество <= 0, удаляем элемент
                await session.delete(cart_item)
                await session.commit()
                return {
                    "message": "Item removed from cart (quantity <= 0)",
                    "item_id": item_id,
                    "action": "removed"
                }
            
            cart_item.quantity = new_quantity
            cart_item.added_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(cart_item)
        
        return {
            **cart_item.to_dict(),
            "message": "Cart item updated",
            "action": "updated"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in update_cart_item: {e}")
        print(traceback.format_exc())
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_cart(
    item_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Удалить элемент из корзины
    """
    try:
        query = select(CartItemModel).where(CartItemModel.id == item_id)
        result = await session.execute(query)
        cart_item = result.scalar_one_or_none()
        
        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found"
            )
        
        await session.delete(cart_item)
        await session.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in remove_from_cart: {e}")
        print(traceback.format_exc())
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/user/{user_id}/clear", status_code=status.HTTP_204_NO_CONTENT)
async def clear_user_cart(
    user_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Очистить корзину пользователя
    """
    try:
        query = select(CartItemModel).where(CartItemModel.user_id == user_id)
        result = await session.execute(query)
        cart_items = result.scalars().all()
        
        for item in cart_items:
            await session.delete(item)
        
        await session.commit()
        
    except Exception as e:
        print(f"Error in clear_user_cart: {e}")
        print(traceback.format_exc())
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/user/{user_id}/merge", response_model=dict)
async def merge_carts(
    user_id: int,
    cart_session_id: str = Query(..., description="ID сессии для объединения"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Объединить корзину неавторизованного пользователя с корзиной пользователя
    """
    try:
        # Получаем элементы из сессионной корзины
        session_cart_query = select(CartItemModel).where(
            and_(
                CartItemModel.cart_session_id == cart_session_id,
                CartItemModel.user_id.is_(None)  # Только неавторизованные
            )
        )
        session_result = await session.execute(session_cart_query)
        session_items = session_result.scalars().all()
        
        if not session_items:
            return {
                "message": "No items to merge",
                "merged_count": 0
            }
        
        merged_count = 0
        
        for session_item in session_items:
            # Проверяем, есть ли уже такой товар в корзине пользователя
            user_item_query = select(CartItemModel).where(
                and_(
                    CartItemModel.user_id == user_id,
                    or_(
                        CartItemModel.product_id == session_item.product_id,
                        CartItemModel.listing_id == session_item.listing_id,
                        CartItemModel.author_listing_id == session_item.author_listing_id
                    )
                )
            )
            user_result = await session.execute(user_item_query)
            user_item = user_result.scalar_one_or_none()
            
            if user_item:
                # Объединяем количество
                user_item.quantity += session_item.quantity
                merged_count += 1
            else:
                # Переносим элемент
                session_item.user_id = user_id
                session_item.cart_session_id = None
                merged_count += 1
        
        await session.commit()
        
        return {
            "message": "Carts merged successfully",
            "merged_count": merged_count,
            "user_id": user_id
        }
        
    except Exception as e:
        print(f"Error in merge_carts: {e}")
        print(traceback.format_exc())
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/summary/{user_id}", response_model=dict)
async def get_cart_summary(
    user_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить сводку по корзине (количество товаров, общая стоимость)
    """
    try:
        from sqlalchemy import func
        
        # Получаем элементы корзины с продуктами
        query = (
            select(CartItemModel, ProductModel)
            .join(ProductModel, CartItemModel.product_id == ProductModel.id)
            .where(CartItemModel.user_id == user_id)
            .where(CartItemModel.product_id.isnot(None))
        )
        
        result = await session.execute(query)
        items_with_products = result.all()
        
        total_items = 0
        total_quantity = 0
        total_price = 0.0
        items_summary = []
        
        for cart_item, product in items_with_products:
            if product.price:
                subtotal = float(product.price) * cart_item.quantity
                total_price += subtotal
                total_quantity += cart_item.quantity
                total_items += 1
                
                items_summary.append({
                    "id": cart_item.id,
                    "product_id": product.id,
                    "title": product.title,
                    "quantity": cart_item.quantity,
                    "price": float(product.price),
                    "subtotal": subtotal,
                    "image_url": product.image_url
                })
        
        return {
            "user_id": user_id,
            "summary": {
                "total_items": total_items,
                "total_quantity": total_quantity,
                "total_price": round(total_price, 2),
                "items": items_summary
            }
        }
        
    except Exception as e:
        print(f"Error in get_cart_summary: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/count/{user_id}", response_model=dict)
async def get_cart_count(
    user_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить количество товаров в корзине
    """
    try:
        from sqlalchemy import func
        
        # Подсчитываем общее количество товаров
        count_query = select(func.count(CartItemModel.id)).where(CartItemModel.user_id == user_id)
        count_result = await session.execute(count_query)
        total_items = count_result.scalar() or 0
        
        # Подсчитываем общее количество единиц
        quantity_query = select(func.sum(CartItemModel.quantity)).where(CartItemModel.user_id == user_id)
        quantity_result = await session.execute(quantity_query)
        total_quantity = quantity_result.scalar() or 0
        
        return {
            "user_id": user_id,
            "total_items": total_items,
            "total_quantity": total_quantity,
            "has_items": total_items > 0
        }
        
    except Exception as e:
        print(f"Error in get_cart_count: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/health")
async def cart_health_check(session: AsyncSession = Depends(get_async_session)):
    """
    Проверка работоспособности корзины
    """
    try:
        # Проверяем подключение к БД
        result = await session.execute(select(func.count(CartItemModel.id)))
        count = result.scalar()
        
        return {
            "status": "healthy",
            "service": "cart-api",
            "database": "connected",
            "total_cart_items": count or 0,
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