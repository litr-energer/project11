from typing import Any, Optional, Dict
from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    """Базовое исключение для всех кастомных исключений API"""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None,
        extra: Optional[Dict[str, Any]] = None
    ):
        self.error_code = error_code or f"ERR_{status_code}"
        self.extra = extra or {}
        
        # Формируем детальное сообщение с дополнительной информацией
        full_detail = {
            "error": detail,
            "error_code": self.error_code,
            **self.extra
        }
        
        super().__init__(status_code=status_code, detail=full_detail, headers=headers)


class NotFoundException(BaseAPIException):
    """Исключение для случаев, когда ресурс не найден"""
    
    def __init__(self, resource_name: str, resource_id: Any, **kwargs):
        detail = f"{resource_name} with ID {resource_id} not found"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="NOT_FOUND",
            extra={"resource": resource_name, "resource_id": resource_id},
            **kwargs
        )


class BadRequestException(BaseAPIException):
    """Исключение для некорректных запросов"""
    
    def __init__(self, detail: str = "Bad request", **kwargs):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="BAD_REQUEST",
            **kwargs
        )


class UnauthorizedException(BaseAPIException):
    """Исключение для неавторизованных запросов"""
    
    def __init__(self, detail: str = "Unauthorized", **kwargs):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="UNAUTHORIZED",
            **kwargs
        )


class ForbiddenException(BaseAPIException):
    """Исключение для запрещенных действий"""
    
    def __init__(self, detail: str = "Forbidden", **kwargs):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="FORBIDDEN",
            **kwargs
        )


class ConflictException(BaseAPIException):
    """Исключение для конфликтующих данных"""
    
    def __init__(self, detail: str = "Conflict", **kwargs):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code="CONFLICT",
            **kwargs
        )


class ValidationException(BaseAPIException):
    """Исключение для ошибок валидации"""
    
    def __init__(self, detail: str = "Validation error", errors: Optional[list] = None, **kwargs):
        extra = {"validation_errors": errors} if errors else {}
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR",
            extra=extra,
            **kwargs
        )


class InternalServerError(BaseAPIException):
    """Исключение для внутренних ошибок сервера"""
    
    def __init__(self, detail: str = "Internal server error", **kwargs):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="INTERNAL_ERROR",
            **kwargs
        )