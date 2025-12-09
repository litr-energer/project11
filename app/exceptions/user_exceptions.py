from .base_exceptions import NotFoundException, ConflictException, ValidationException, UnauthorizedException


class UserNotFoundException(NotFoundException):
    """Исключение, когда пользователь не найден"""
    
    def __init__(self, user_id: int = None, email: str = None):
        if user_id:
            super().__init__(resource_name="User", resource_id=user_id)
        elif email:
            detail = f"User with email '{email}' not found"
            super().__init__(
                status_code=404,
                detail=detail,
                error_code="USER_NOT_FOUND",
                extra={"email": email}
            )
        else:
            super().__init__(resource_name="User", resource_id="unknown")


class UserAlreadyExistsException(ConflictException):
    """Исключение, когда пользователь с таким email уже существует"""
    
    def __init__(self, email: str):
        detail = f"User with email '{email}' already exists"
        super().__init__(
            detail=detail,
            error_code="USER_ALREADY_EXISTS",
            extra={"email": email}
        )


class InvalidCredentialsException(UnauthorizedException):
    """Исключение для неверных учетных данных"""
    
    def __init__(self):
        detail = "Invalid email or password"
        super().__init__(
            detail=detail,
            error_code="INVALID_CREDENTIALS"
        )


class UserValidationException(ValidationException):
    """Исключение для ошибок валидации пользователя"""
    
    def __init__(self, detail: str = "User validation error", errors: list = None):
        super().__init__(detail=detail, errors=errors, error_code="USER_VALIDATION_ERROR")