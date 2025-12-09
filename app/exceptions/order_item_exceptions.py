from .base_exceptions import NotFoundException, ValidationException


class OrderItemNotFoundException(NotFoundException):
    """Исключение, когда элемент заказа не найден"""
    
    def __init__(self, order_item_id: int):
        super().__init__(resource_name="OrderItem", resource_id=order_item_id)


class OrderItemValidationException(ValidationException):
    """Исключение для ошибок валидации элемента заказа"""
    
    def __init__(self, detail: str = "Order item validation error", errors: list = None):
        super().__init__(detail=detail, errors=errors, error_code="ORDER_ITEM_VALIDATION_ERROR")