from .base_exceptions import NotFoundException, ValidationException


class ChatMessageNotFoundException(NotFoundException):
    """Исключение, когда сообщение чата не найдено"""
    
    def __init__(self, message_id: int):
        super().__init__(resource_name="ChatMessage", resource_id=message_id)


class ChatValidationException(ValidationException):
    """Исключение для ошибок валидации чата"""
    
    def __init__(self, detail: str = "Chat validation error", errors: list = None):
        super().__init__(detail=detail, errors=errors, error_code="CHAT_VALIDATION_ERROR")