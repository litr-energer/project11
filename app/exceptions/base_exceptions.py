from typing import Any, Dict, Optional
from fastapi import HTTPException
from fastapi.responses import JSONResponse

class BaseAPIException(Exception):
    """Базовый класс для всех кастомных исключений API"""
    
    def __init__(
        self,
        status_code: int = 400,
        error_code: str = "api_error",
        detail: Any = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.status_code = status_code
        self.error_code = error_code
        self.detail = detail
        self.headers = headers
        
        if detail is None:
            self.detail = "Произошла ошибка API"
            
        super().__init__(self.detail)

# ======= ДОБАВЬТЕ ЭТИ КЛАССЫ =======

class NotFoundException(BaseAPIException):
    """Исключение когда ресурс не найден"""
    
    def __init__(self, resource_name: str, resource_id: str = None):
        self.resource_name = resource_name
        self.resource_id = resource_id
        
        if resource_id:
            detail = f"{resource_name} with ID {resource_id} not found"
        else:
            detail = f"{resource_name} not found"
            
        super().__init__(
            status_code=404,
            error_code="not_found",
            detail=detail
        )

class ValidationException(BaseAPIException):
    """Исключение для ошибок валидации"""
    
    def __init__(self, detail: str = "Validation error", errors: list = None):
        self.errors = errors or []
        
        super().__init__(
            status_code=400,
            error_code="validation_error",
            detail=detail
        )

class BadRequestException(BaseAPIException):
    """Исключение для ошибок запроса"""
    
    def __init__(self, detail: str = "Bad request", error_code: str = None, extra: dict = None):
        super().__init__(
            status_code=400,
            error_code=error_code or "bad_request",
            detail=detail
        )
        self.extra = extra or {}

# ===================================

class APIException(HTTPException):
    """HTTP исключение для использования в FastAPI роутерах"""
    
    def __init__(
        self,
        status_code: int,
        error_code: str,
        detail: Any = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.error_code = error_code
        if detail is None:
            detail = "Произошла ошибка"
            
        super().__init__(status_code=status_code, detail=detail, headers=headers)

def handle_api_exception(exc: BaseAPIException):
    """Обработчик для BaseAPIException"""
    content = {
        "error_code": exc.error_code,
        "detail": exc.detail,
    }
    return JSONResponse(
        status_code=exc.status_code,
        content=content,
        headers=exc.headers,
    )