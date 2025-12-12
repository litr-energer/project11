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