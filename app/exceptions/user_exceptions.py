from app.exceptions.base_exceptions import BaseAPIException

class UserNotFoundException(BaseAPIException):
    """Исключение: пользователь не найден"""
    
    def __init__(self, user_id: int = None, email: str = None, detail: str = None):
        if detail is None:
            if user_id:
                detail = f"Пользователь с ID {user_id} не найден"
            elif email:
                detail = f"Пользователь с email {email} не найден"
            else:
                detail = "Пользователь не найден"
                
        super().__init__(
            status_code=404,
            error_code="user_not_found",
            detail=detail
        )

class UserAlreadyExistsException(BaseAPIException):
    """Исключение: пользователь уже существует"""
    
    def __init__(self, email: str = None, detail: str = None):
        if detail is None:
            if email:
                detail = f"Пользователь с email {email} уже существует"
            else:
                detail = "Пользователь уже существует"
                
        super().__init__(
            status_code=409,
            error_code="user_already_exists",
            detail=detail
        )

class InvalidCredentialsException(BaseAPIException):
    """Исключение: неверные учетные данные"""
    
    def __init__(self, detail: str = None):
        if detail is None:
            detail = "Неверный email или пароль"
            
        super().__init__(
            status_code=401,
            error_code="invalid_credentials",
            detail=detail
        )

class InsufficientPermissionsException(BaseAPIException):
    """Исключение: недостаточно прав"""
    
    def __init__(self, detail: str = None):
        if detail is None:
            detail = "Недостаточно прав для выполнения операции"
            
        super().__init__(
            status_code=403,
            error_code="insufficient_permissions",
            detail=detail
        )