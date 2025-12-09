from typing import Optional
from app.repositories.cart_repository import CartRepository
from app.repositories.cart_item_repository import CartItemRepository
from app.services.service import BaseService
from app.models.carts import CartModel
from app.models.cart_items import CartItemModel

class CartService(BaseService[CartModel]):
    def __init__(self, cart_repository: CartRepository, cart_item_repository: CartItemRepository):
        super().__init__(cart_repository)
        self.cart_repository = cart_repository
        self.cart_item_repository = cart_item_repository
    
    def get_or_create_user_cart(self, user_id: int) -> CartModel:
        cart = self.cart_repository.get_by_user(user_id)
        if not cart:
            cart = self.cart_repository.create({"user_id": user_id})
        return cart
    
    def get_cart_items(self, cart_id: int, skip: int = 0, limit: int = 100):
        return self.cart_item_repository.get_by_cart(cart_id, skip, limit)
    
    def add_item_to_cart(self, cart_id: int, item_data: dict) -> CartItemModel:
        return self.cart_item_repository.create({**item_data, "cart_id": cart_id})
    
    def remove_item_from_cart(self, item_id: int) -> bool:
        return self.cart_item_repository.delete(item_id)
    
    def update_cart_item_quantity(self, item_id: int, quantity: int) -> Optional[CartItemModel]:
        return self.cart_item_repository.update(item_id, {"quantity": quantity})
    
    def clear_cart(self, cart_id: int) -> bool:
        items = self.cart_item_repository.get_by_cart(cart_id)
        for item in items:
            self.cart_item_repository.delete(item.id)
        return True