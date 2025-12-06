# app/api/orders.py (исправленная версия без сложных связей)
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_, or_, desc, asc
from datetime import datetime, timedelta
from decimal import Decimal
import traceback

from app.database.database import get_async_session
from app.models.orders import OrderModel
from app.models.order_items import OrderItemModel
from app.models.products import ProductModel

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


@router.get("/", response_model=List[dict])
async def get_orders(
    user_id: Optional[int] = Query(None, description="Фильтр по пользователю"),
    status: Optional[str] = Query(None, description="Фильтр по статусу"),
    start_date: Optional[datetime] = Query(None, description="Начальная дата"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    order_by: str = Query("desc", description="Порядок сортировки: asc или desc"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить список заказов
    """
    try:
        query = select(OrderModel)
        
        if user_id:
            query = query.where(OrderModel.user_id == user_id)
        
        if status:
            query = query.where(OrderModel.status == status)
        
        if start_date:
            query = query.where(OrderModel.created_at >= start_date)
        
        if end_date:
            query = query.where(OrderModel.created_at <= end_date)
        
        if order_by.lower() == "asc":
            query = query.order_by(asc(OrderModel.created_at))
        else:
            query = query.order_by(desc(OrderModel.created_at))
        
        query = query.offset(skip).limit(limit)
        
        result = await session.execute(query)
        orders = result.scalars().all()
        
        return [order.to_dict() for order in orders]
        
    except Exception as e:
        print(f"Error in get_orders: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{order_id}", response_model=dict)
async def get_order(
    order_id: int,
    with_items: bool = Query(True, description="Включить элементы заказа"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить заказ по ID
    """
    try:
        query = select(OrderModel).where(OrderModel.id == order_id)
        result = await session.execute(query)
        order = result.scalar_one_or_none()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        order_dict = order.to_dict()
        
        if with_items:
            items_query = select(OrderItemModel).where(OrderItemModel.order_id == order_id)
            items_result = await session.execute(items_query)
            order_items = items_result.scalars().all()
            
            order_dict["items"] = [item.to_dict() for item in order_items]
            
            # Подсчитываем общее количество товаров
            total_quantity = sum(item.quantity for item in order_items)
            order_dict["total_quantity"] = total_quantity
        
        return order_dict
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_order: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: dict,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Создать новый заказ
    """
    try:
        # Проверяем обязательные поля
        required_fields = ['user_id', 'customer_name', 'customer_email', 'payment_method']
        for field in required_fields:
            if field not in order_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required field: {field}"
                )
        
        if 'items' not in order_data or not order_data['items']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order must contain at least one item"
            )
        
        # Рассчитываем общую сумму
        total_amount = Decimal('0.0')
        for item in order_data['items']:
            if 'product_price' not in item or 'quantity' not in item:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Each item must have product_price and quantity"
                )
            
            price = Decimal(str(item['product_price']))
            quantity = int(item['quantity'])
            subtotal = price * quantity
            total_amount += subtotal
        
        # Создаем заказ
        order = OrderModel(
            user_id=order_data['user_id'],
            total_amount=total_amount,
            status="pending",
            customer_name=order_data['customer_name'],
            customer_email=order_data['customer_email'],
            customer_phone=order_data.get('customer_phone'),
            shipping_address=order_data.get('shipping_address'),
            billing_address=order_data.get('billing_address'),
            payment_method=order_data['payment_method'],
            payment_status="pending",
            payment_data=order_data.get('payment_data'),
            notes=order_data.get('notes'),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        session.add(order)
        await session.commit()
        await session.refresh(order)
        
        # Создаем элементы заказа
        for item_data in order_data['items']:
            price = Decimal(str(item_data['product_price']))
            quantity = int(item_data['quantity'])
            subtotal = price * quantity
            
            order_item = OrderItemModel(
                order_id=order.id,
                product_id=item_data.get('product_id'),
                product_name=item_data['product_name'],
                product_price=price,
                quantity=quantity,
                subtotal=subtotal,
                product_image_url=item_data.get('product_image_url'),
                product_description=item_data.get('product_description')
            )
            
            session.add(order_item)
        
        await session.commit()
        
        # Получаем созданные элементы заказа
        items_query = select(OrderItemModel).where(OrderItemModel.order_id == order.id)
        items_result = await session.execute(items_query)
        order_items = items_result.scalars().all()
        
        order_dict = order.to_dict()
        order_dict["items"] = [item.to_dict() for item in order_items]
        
        return {
            **order_dict,
            "message": "Order created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in create_order: {e}")
        print(traceback.format_exc())
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.put("/{order_id}/status", response_model=dict)
async def update_order_status(
    order_id: int,
    status_data: dict,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Обновить статус заказа
    """
    try:
        query = select(OrderModel).where(OrderModel.id == order_id)
        result = await session.execute(query)
        order = result.scalar_one_or_none()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        if 'status' in status_data:
            order.status = status_data['status']
        
        if 'payment_status' in status_data:
            order.payment_status = status_data['payment_status']
        
        if 'payment_data' in status_data:
            order.payment_data = status_data['payment_data']
        
        order.updated_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(order)
        
        return {
            **order.to_dict(),
            "message": "Order status updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in update_order_status: {e}")
        print(traceback.format_exc())
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=List[dict])
async def get_user_orders(
    user_id: int,
    limit: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить заказы пользователя
    """
    try:
        query = (
            select(OrderModel)
            .where(OrderModel.user_id == user_id)
            .order_by(desc(OrderModel.created_at))
            .limit(limit)
        )
        
        result = await session.execute(query)
        orders = result.scalars().all()
        
        return [order.to_dict() for order in orders]
        
    except Exception as e:
        print(f"Error in get_user_orders: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{order_id}/items", response_model=List[dict])
async def get_order_items(
    order_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить элементы заказа
    """
    try:
        order_query = select(OrderModel).where(OrderModel.id == order_id)
        order_result = await session.execute(order_query)
        order = order_result.scalar_one_or_none()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        items_query = select(OrderItemModel).where(OrderItemModel.order_id == order_id)
        items_result = await session.execute(items_query)
        order_items = items_result.scalars().all()
        
        return [item.to_dict() for item in order_items]
        
    except Exception as e:
        print(f"Error in get_order_items: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_order(
    order_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Отменить заказ
    """
    try:
        query = select(OrderModel).where(OrderModel.id == order_id)
        result = await session.execute(query)
        order = result.scalar_one_or_none()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        order.status = "cancelled"
        order.payment_status = "cancelled"
        order.updated_at = datetime.utcnow()
        
        await session.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in cancel_order: {e}")
        print(traceback.format_exc())
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/statistics", response_model=dict)
async def get_orders_statistics(
    user_id: Optional[int] = Query(None),
    days: int = Query(30, ge=1, le=365),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить статистику по заказам
    """
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = select(OrderModel).where(OrderModel.created_at >= start_date)
        
        if user_id:
            query = query.where(OrderModel.user_id == user_id)
        
        result = await session.execute(query)
        orders = result.scalars().all()
        
        total_orders = len(orders)
        total_amount = sum(float(order.total_amount) for order in orders)
        
        status_counts = {}
        for order in orders:
            status_counts[order.status] = status_counts.get(order.status, 0) + 1
        
        avg_order_amount = total_amount / total_orders if total_orders > 0 else 0
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": datetime.utcnow().isoformat(),
                "days": days
            },
            "user_id": user_id,
            "statistics": {
                "total_orders": total_orders,
                "total_amount": round(total_amount, 2),
                "average_order_amount": round(avg_order_amount, 2),
                "orders_by_status": status_counts
            }
        }
        
    except Exception as e:
        print(f"Error in get_orders_statistics: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/health")
async def orders_health_check(session: AsyncSession = Depends(get_async_session)):
    """
    Проверка работоспособности
    """
    try:
        result = await session.execute(select(func.count(OrderModel.id)))
        count = result.scalar()
        
        return {
            "status": "healthy",
            "service": "orders-api",
            "database": "connected",
            "total_orders": count or 0,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "orders-api",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }