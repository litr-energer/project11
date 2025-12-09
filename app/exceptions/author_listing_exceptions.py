from .base_exceptions import NotFoundException, ValidationException, BadRequestException


class AuthorListingNotFoundException(NotFoundException):
    """Исключение, когда авторский листинг не найден"""
    
    def __init__(self, author_listing_id: int):
        super().__init__(resource_name="AuthorListing", resource_id=author_listing_id)


class AuthorListingValidationException(ValidationException):
    """Исключение для ошибок валидации авторского листинга"""
    
    def __init__(self, detail: str = "Author listing validation error", errors: list = None):
        super().__init__(detail=detail, errors=errors, error_code="AUTHOR_LISTING_VALIDATION_ERROR")


class AuthorListingInactiveException(BadRequestException):
    """Исключение, когда авторский листинг неактивен"""
    
    def __init__(self, author_listing_id: int):
        detail = f"Author listing with ID {author_listing_id} is inactive"
        super().__init__(
            detail=detail,
            error_code="AUTHOR_LISTING_INACTIVE",
            extra={"author_listing_id": author_listing_id}
        )