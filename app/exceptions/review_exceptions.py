from .base_exceptions import NotFoundException, ValidationException, ConflictException, BadRequestException


class ReviewNotFoundException(NotFoundException):
    """Исключение, когда отзыв не найден"""
    
    def __init__(self, review_id: int):
        super().__init__(resource_name="Review", resource_id=review_id)


class ReviewValidationException(ValidationException):
    """Исключение для ошибок валидации отзыва"""
    
    def __init__(self, detail: str = "Review validation error", errors: list = None):
        super().__init__(detail=detail, errors=errors, error_code="REVIEW_VALIDATION_ERROR")


class ReviewRatingException(BadRequestException):
    """Исключение для ошибок рейтинга"""
    
    def __init__(self, rating: int):
        detail = f"Rating {rating} is invalid. Must be between 1 and 5"
        super().__init__(
            detail=detail,
            error_code="REVIEW_RATING_ERROR",
            extra={"rating": rating}
        )


class ReviewAlreadyExistsException(ConflictException):
    """Исключение, когда отзыв уже существует"""
    
    def __init__(self, user_id: int, item_type: str, item_id: int):
        detail = f"Review already exists for item {item_id} of type {item_type} by user {user_id}"
        super().__init__(
            detail=detail,
            error_code="REVIEW_ALREADY_EXISTS",
            extra={
                "user_id": user_id,
                "item_type": item_type,
                "item_id": item_id
            }
        )