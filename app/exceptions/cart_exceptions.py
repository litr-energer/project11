# app/exceptions/cart_exceptions.py
from .base_exceptions import NotFoundException, ValidationException, BadRequestException


class CartNotFoundException(NotFoundException):
    """Исключение, когда корзина не найдена"""
    
    def __init__(self, cart_id: int = None, user_id: int = None):
        if cart_id:
            super().__init__(resource_name="Cart", resource_id=str(cart_id))
        elif user_id:
            detail = f"Cart for user with ID {user_id} not found"
            super().__init__(
                status_code=404,
                error_code="cart_not_found",
                detail=detail
            )
            self.extra = {"user_id": user_id}
        else:
            super().__init__(resource_name="Cart")


class CartItemNotFoundException(NotFoundException):
    """Исключение, когда элемент корзины не найден"""
    
    def __init__(self, cart_item_id: int):
        super().__init__(resource_name="CartItem", resource_id=str(cart_item_id))


class CartValidationException(ValidationException):
    """Исключение для ошибок валидации корзины"""
    
    def __init__(self, detail: str = "Cart validation error", errors: list = None):
        super().__init__(detail=detail, errors=errors)


class EmptyCartException(BadRequestException):
    """Исключение, когда корзина пуста"""
    
    def __init__(self, cart_id: int):
        detail = f"Cart with ID {cart_id} is empty"
        super().__init__(
            detail=detail,
            error_code="cart_empty"
        )
        self.extra = {"cart_id": cart_id}