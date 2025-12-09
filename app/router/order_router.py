from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas import Order, OrderCreate, OrderUpdate
from app.services.order_service import OrderService
from app.repositories.order_repository import OrderRepository

router = APIRouter(prefix="/orders", tags=["orders"])

def get_order_service(db: Session = Depends(get_db)) -> OrderService:
    order_repository = OrderRepository(db)
    return OrderService(order_repository)

@router.get("/", response_model=List[Order])
def get_orders(
    skip: int = 0,
    limit: int = 100,
    user_id: int = None,
    status: str = None,
    order_service: OrderService = Depends(get_order_service)
):
    if user_id:
        return order_service.get_by_user(user_id, skip, limit)
    elif status:
        return order_service.get_by_status(status, skip, limit)
    else:
        return order_service.get_all(skip, limit)

@router.get("/{order_id}", response_model=Order)
def get_order(
    order_id: int,
    order_service: OrderService = Depends(get_order_service)
):
    order = order_service.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.post("/", response_model=Order)
def create_order(
    order_data: OrderCreate,
    order_service: OrderService = Depends(get_order_service)
):
    return order_service.create(order_data.dict())

@router.put("/{order_id}", response_model=Order)
def update_order(
    order_id: int,
    order_data: OrderUpdate,
    order_service: OrderService = Depends(get_order_service)
):
    order = order_service.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return order_service.update(order_id, order_data.dict(exclude_unset=True))

@router.delete("/{order_id}")
def delete_order(
    order_id: int,
    order_service: OrderService = Depends(get_order_service)
):
    success = order_service.delete(order_id)
    if not success:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order deleted successfully"}

@router.patch("/{order_id}/status")
def update_order_status(
    order_id: int,
    status: str,
    order_service: OrderService = Depends(get_order_service)
):
    order = order_service.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order_service.update_status(order_id, status)
    return {"message": f"Order status updated to {status}"}