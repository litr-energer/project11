import logging
from typing import Union
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from .base_exceptions import BaseAPIException, InternalServerError

# Настройка логгера
logger = logging.getLogger(__name__)


async def base_api_exception_handler(request: Request, exc: BaseAPIException) -> JSONResponse:
    """Обработчик для кастомных исключений API"""
    logger.error(f"API Exception: {exc.detail}", exc_info=exc)
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail,
        headers=exc.headers
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Обработчик для ошибок валидации Pydantic"""
    errors = []
    for error in exc.errors():
        errors.append({
            "loc": error.get("loc"),
            "msg": error.get("msg"),
            "type": error.get("type")
        })
    
    logger.warning(f"Validation error: {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation error",
            "error_code": "VALIDATION_ERROR",
            "validation_errors": errors
        }
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Обработчик для ошибок SQLAlchemy"""
    logger.error(f"Database error: {str(exc)}", exc_info=exc)
    
    # Обработка ошибок целостности (уникальность, внешние ключи)
    if isinstance(exc, IntegrityError):
        # Попробуем извлечь детали из сообщения об ошибке
        error_msg = str(exc.orig) if hasattr(exc, 'orig') else str(exc)
        
        # Проверяем на нарушение уникальности
        if "unique" in error_msg.lower() or "duplicate" in error_msg.lower():
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={
                    "error": "Duplicate entry",
                    "error_code": "DUPLICATE_ENTRY",
                    "detail": "Resource already exists"
                }
            )
        # Проверяем на нарушение внешнего ключа
        elif "foreign key" in error_msg.lower():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "error": "Foreign key violation",
                    "error_code": "FOREIGN_KEY_VIOLATION",
                    "detail": "Referenced resource does not exist"
                }
            )
    
    # Общая ошибка базы данных
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Database error",
            "error_code": "DATABASE_ERROR",
            "detail": "An error occurred while processing your request"
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Обработчик для всех необработанных исключений"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=exc)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "detail": "An unexpected error occurred"
        }
    )


def setup_exception_handlers(app: FastAPI):
    """Настройка обработчиков исключений для FastAPI приложения"""
    
    # Регистрируем обработчик для кастомных исключений
    app.add_exception_handler(BaseAPIException, base_api_exception_handler)
    
    # Регистрируем обработчик для ошибок валидации
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # Регистрируем обработчик для ошибок SQLAlchemy
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    
    # Регистрируем общий обработчик для всех остальных исключений
    app.add_exception_handler(Exception, general_exception_handler)