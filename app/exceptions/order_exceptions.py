from .base_exceptions import NotFoundException, ValidationException, BadRequestException


class OrderNotFoundException(NotFoundException):
    """Исключение, когда заказ не найден"""
    
    def __init__(self, order_id: int):
        super().__init__(resource_name="Order", resource_id=order_id)


class OrderValidationException(ValidationException):
    """Исключение для ошибок валидации заказа"""
    
    def __init__(self, detail: str = "Order validation error", errors: list = None):
        super().__init__(detail=detail, errors=errors, error_code="ORDER_VALIDATION_ERROR")


class OrderStatusException(BadRequestException):
    """Исключение для ошибок статуса заказа"""
    
    def __init__(self, order_id: int, current_status: str, target_status: str):
        detail = f"Cannot change order {order_id} status from '{current_status}' to '{target_status}'"
        super().__init__(
            detail=detail,
            error_code="ORDER_STATUS_ERROR",
            extra={
                "order_id": order_id,
                "current_status": current_status,
                "target_status": target_status
            }
        )