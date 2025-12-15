from datetime import datetime
from typing import Dict, Any, Optional
from app.repositories.cart_repository import CartRepository
from app.repositories.cart_item_repository import CartItemRepository
from app.services.service import BaseService
from app.models.carts import CartModel
from app.models.cart_items import CartItemModel
from app.exceptions.cart_exceptions import CartNotFoundException, CartItemNotFoundException


class CartService(BaseService[CartModel]):
    def __init__(self, cart_repository: CartRepository, cart_item_repository: CartItemRepository):
        super().__init__(cart_repository)
        self.cart_repository = cart_repository
        self.cart_item_repository = cart_item_repository
    
    def get_or_create_user_cart(self, user_id: int) -> CartModel:
        """Получаем корзину пользователя или создаем новую"""
        cart = self.cart_repository.get_by_user(user_id)
        if not cart:
            # Создаем новую корзину
            cart_data = {"user_id": user_id}
            cart = self.cart_repository.create(cart_data)
        return cart
    
    def get_cart_items(self, cart_id: int, skip: int = 0, limit: int = 100) -> list:
        """Получаем элементы корзины"""
        cart = self.get(cart_id)
        if not cart:
            raise CartNotFoundException(cart_id=cart_id)
        
        return self.cart_item_repository.get_by_cart_id(cart_id, skip, limit)
    
    def add_item_to_cart(self, cart_id: int, item_data: Dict[str, Any]) -> CartItemModel:
        """Добавляем товар в корзину"""
        cart = self.get(cart_id)
        if not cart:
            raise CartNotFoundException(cart_id=cart_id)
        
        # Определяем тип товара
        item_type = item_data.get('item_type')
        if not item_type:
            # Определяем тип автоматически
            if item_data.get('product_id'):
                item_type = 'product'
                item_id = item_data['product_id']
            elif item_data.get('listing_id'):
                item_type = 'listing'
                item_id = item_data['listing_id']
            elif item_data.get('author_listing_id'):
                item_type = 'author_listing'
                item_id = item_data['author_listing_id']
            else:
                raise ValueError("Item type cannot be determined")
        else:
            item_id = item_data.get(f'{item_type}_id')
        
        # Проверяем, есть ли уже такой товар в корзине
        existing_item = self.cart_item_repository.get_by_cart_and_item(cart_id, item_type, item_id)
        
        if existing_item:
            # Обновляем количество
            existing_item.quantity += item_data.get('quantity', 1)
            existing_item.price = item_data.get('price', existing_item.price)
            self.db.commit()
            self.db.refresh(existing_item)
            return existing_item
        else:
            # Создаем новый элемент
            cart_item_data = {
                "cart_id": cart_id,
                "item_type": item_type,
                f"{item_type}_id": item_id,
                "quantity": item_data.get('quantity', 1),
                "price": item_data.get('price', 0)
            }
            return self.cart_item_repository.create(cart_item_data)
    
    def update_cart_item_quantity(self, item_id: int, quantity: int) -> Optional[CartItemModel]:
        """Обновляем количество товара в корзине"""
        item = self.cart_item_repository.get(item_id)
        if not item:
            raise CartItemNotFoundException(item_id)
        
        if quantity <= 0:
            # Удаляем товар если количество 0 или меньше
            self.cart_item_repository.delete(item_id)
            return None
        
        update_data = {"quantity": quantity}
        return self.cart_item_repository.update(item_id, update_data)
    
    def remove_item_from_cart(self, item_id: int) -> bool:
        """Удаляем товар из корзины"""
        return self.cart_item_repository.delete(item_id)
    
    def clear_cart(self, cart_id: int) -> bool:
        """Очищаем корзину"""
        cart = self.get(cart_id)
        if not cart:
            raise CartNotFoundException(cart_id=cart_id)
        
        # Удаляем все элементы корзины
        items = self.cart_item_repository.get_by_cart_id(cart_id)
        for item in items:
            self.cart_item_repository.delete(item.id)
        
        # Обновляем время изменения корзины
        self.cart_repository.update(cart_id, {"updated_at": datetime.utcnow()})
        return True
    
    def get_cart_total(self, cart_id: int) -> float:
        """Получаем общую стоимость корзины"""
        items = self.get_cart_items(cart_id)
        total = 0.0
        for item in items:
            total += item.price * item.quantity
        return total