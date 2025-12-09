from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas import Cart, CartItem, CartItemCreate, CartItemUpdate
from app.services.cart_service import CartService
from app.repositories.cart_repository import CartRepository
from app.repositories.cart_item_repository import CartItemRepository

router = APIRouter(prefix="/carts", tags=["carts"])

def get_cart_service(db: Session = Depends(get_db)) -> CartService:
    cart_repository = CartRepository(db)
    cart_item_repository = CartItemRepository(db)
    return CartService(cart_repository, cart_item_repository)

@router.get("/user/{user_id}", response_model=Cart)
def get_user_cart(
    user_id: int,
    cart_service: CartService = Depends(get_cart_service)
):
    return cart_service.get_or_create_user_cart(user_id)

@router.get("/{cart_id}/items", response_model=List[CartItem])
def get_cart_items(
    cart_id: int,
    skip: int = 0,
    limit: int = 100,
    cart_service: CartService = Depends(get_cart_service)
):
    return cart_service.get_cart_items(cart_id, skip, limit)

@router.post("/{cart_id}/items", response_model=CartItem)
def add_item_to_cart(
    cart_id: int,
    item_data: CartItemCreate,
    cart_service: CartService = Depends(get_cart_service)
):
    # Проверяем, что указан хотя бы один тип товара
    if not any([item_data.product_id, item_data.listing_id, item_data.author_listing_id]):
        raise HTTPException(
            status_code=400, 
            detail="At least one of product_id, listing_id, or author_listing_id must be provided"
        )
    
    return cart_service.add_item_to_cart(cart_id, item_data.dict())

@router.put("/items/{item_id}", response_model=CartItem)
def update_cart_item(
    item_id: int,
    item_data: CartItemUpdate,
    cart_service: CartService = Depends(get_cart_service)
):
    item = cart_service.cart_item_repository.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    return cart_service.update_cart_item_quantity(item_id, item_data.quantity)

@router.delete("/items/{item_id}")
def remove_item_from_cart(
    item_id: int,
    cart_service: CartService = Depends(get_cart_service)
):
    success = cart_service.remove_item_from_cart(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return {"message": "Item removed from cart"}

@router.delete("/{cart_id}/clear")
def clear_cart(
    cart_id: int,
    cart_service: CartService = Depends(get_cart_service)
):
    cart = cart_service.get(cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    cart_service.clear_cart(cart_id)
    return {"message": "Cart cleared successfully"}