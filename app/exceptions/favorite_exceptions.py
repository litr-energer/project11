from app.exceptions.base_exceptions import BaseAPIException

class FavoriteNotFoundException(BaseAPIException):
    """Исключение: избранное не найдено"""
    
    def __init__(self, favorite_id: int = None, detail: str = None):
        if detail is None:
            if favorite_id:
                detail = f"Избранное с ID {favorite_id} не найдено"
            else:
                detail = "Избранное не найдено"
                
        super().__init__(
            status_code=404,
            error_code="favorite_not_found",
            detail=detail
        )

class FavoriteAlreadyExistsException(BaseAPIException):
    """Исключение: товар уже в избранном"""
    
    def __init__(self, user_id: int = None, item_type: str = None, item_id: int = None, detail: str = None):
        if detail is None:
            if user_id and item_type and item_id:
                detail = f"Товар {item_type} с ID {item_id} уже в избранном у пользователя {user_id}"
            else:
                detail = "Товар уже добавлен в избранное"
                
        super().__init__(
            status_code=409,
            error_code="favorite_already_exists",
            detail=detail
        )

class FavoriteValidationException(BaseAPIException):
    """Исключение: ошибка валидации избранного"""
    
    def __init__(self, detail: str = None):
        if detail is None:
            detail = "Ошибка валидации данных избранного"
            
        super().__init__(
            status_code=400,
            error_code="favorite_validation_error",
            detail=detail
        )