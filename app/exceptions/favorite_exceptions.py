from .base_exceptions import NotFoundException, ConflictException, ValidationException


class FavoriteNotFoundException(NotFoundException):
    """Исключение, когда избранное не найдено"""
    
    def __init__(self, favorite_id: int):
        super().__init__(resource_name="Favorite", resource_id=favorite_id)


class FavoriteAlreadyExistsException(ConflictException):
    """Исключение, когда товар уже в избранном"""
    
    def __init__(self, user_id: int, item_type: str, item_id: int):
        detail = f"Item {item_id} of type {item_type} already in favorites for user {user_id}"
        super().__init__(
            detail=detail,
            error_code="FAVORITE_ALREADY_EXISTS",
            extra={
                "user_id": user_id,
                "item_type": item_type,
                "item_id": item_id
            }
        )


class FavoriteValidationException(ValidationException):
    """Исключение для ошибок валидации избранного"""
    
    def __init__(self, detail: str = "Favorite validation error", errors: list = None):
        super().__init__(detail=detail, errors=errors, error_code="FAVORITE_VALIDATION_ERROR")