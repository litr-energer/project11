from .base_exceptions import NotFoundException, ValidationException, BadRequestException


class ProductNotFoundException(NotFoundException):
    """Исключение, когда продукт не найден"""
    
    def __init__(self, product_id: int):
        super().__init__(resource_name="Product", resource_id=product_id)


class ProductValidationException(ValidationException):
    """Исключение для ошибок валидации продукта"""
    
    def __init__(self, detail: str = "Product validation error", errors: list = None):
        super().__init__(detail=detail, errors=errors, error_code="PRODUCT_VALIDATION_ERROR")


class ProductInactiveException(BadRequestException):
    """Исключение, когда продукт неактивен"""
    
    def __init__(self, product_id: int):
        detail = f"Product with ID {product_id} is inactive"
        super().__init__(
            detail=detail,
            error_code="PRODUCT_INACTIVE",
            extra={"product_id": product_id}
        )