# app/exceptions/handler.py
from typing import Union
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.exceptions.base_exceptions import BaseAPIException, handle_api_exception
from app.exceptions.user_exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidCredentialsException
)

def setup_exception_handlers(app: FastAPI):
    """Настройка обработчиков исключений для приложения"""
    
    @app.exception_handler(BaseAPIException)
    async def base_api_exception_handler(request: Request, exc: BaseAPIException):
        return handle_api_exception(exc)
    
    @app.exception_handler(UserNotFoundException)
    async def user_not_found_handler(request: Request, exc: UserNotFoundException):
        return handle_api_exception(exc)
    
    @app.exception_handler(UserAlreadyExistsException)
    async def user_already_exists_handler(request: Request, exc: UserAlreadyExistsException):
        return handle_api_exception(exc)
    
    @app.exception_handler(InvalidCredentialsException)
    async def invalid_credentials_handler(request: Request, exc: InvalidCredentialsException):
        return handle_api_exception(exc)
    
    # Добавьте обработчики для других исключений по аналогии
    
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        # Логирование ошибки
        print(f"Unhandled exception: {exc}")
        
        return JSONResponse(
            status_code=500,
            content={
                "error_code": "internal_server_error",
                "detail": "Внутренняя ошибка сервера"
            }
        )