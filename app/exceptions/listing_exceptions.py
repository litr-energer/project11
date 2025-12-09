from .base_exceptions import NotFoundException, ValidationException, BadRequestException


class ListingNotFoundException(NotFoundException):
    """Исключение, когда листинг не найден"""
    
    def __init__(self, listing_id: int):
        super().__init__(resource_name="Listing", resource_id=listing_id)


class ListingValidationException(ValidationException):
    """Исключение для ошибок валидации листинга"""
    
    def __init__(self, detail: str = "Listing validation error", errors: list = None):
        super().__init__(detail=detail, errors=errors, error_code="LISTING_VALIDATION_ERROR")


class ListingInactiveException(BadRequestException):
    """Исключение, когда листинг неактивен"""
    
    def __init__(self, listing_id: int):
        detail = f"Listing with ID {listing_id} is inactive"
        super().__init__(
            detail=detail,
            error_code="LISTING_INACTIVE",
            extra={"listing_id": listing_id}
        )