# app/exceptions/listing_exceptions.py
from app.exceptions.base_exceptions import BaseAPIException

class ListingNotFoundException(BaseAPIException):
    """Исключение: публикация не найдена"""
    
    def __init__(self, listing_id: int = None, detail: str = None):
        if detail is None:
            if listing_id:
                detail = f"Публикация с ID {listing_id} не найдена"
            else:
                detail = "Публикация не найдена"
                
        super().__init__(
            status_code=404,
            error_code="listing_not_found",
            detail=detail
        )

class ListingValidationException(BaseAPIException):
    """Исключение: ошибка валидации публикации"""
    
    def __init__(self, detail: str = None):
        if detail is None:
            detail = "Ошибка валидации данных публикации"
            
        super().__init__(
            status_code=400,
            error_code="listing_validation_error",
            detail=detail
        )

class ListingInactiveException(BaseAPIException):
    """Исключение: публикация неактивна"""
    
    def __init__(self, listing_id: int = None, detail: str = None):
        if detail is None:
            if listing_id:
                detail = f"Публикация с ID {listing_id} неактивна"
            else:
                detail = "Публикация неактивна"
                
        super().__init__(
            status_code=400,
            error_code="listing_inactive",
            detail=detail
        )