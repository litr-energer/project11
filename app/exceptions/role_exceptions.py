from app.exceptions.base_exceptions import BaseAPIException

class RoleNotFoundException(BaseAPIException):
    """Исключение: роль не найдена"""
    
    def __init__(self, role_id: int = None, role_name: str = None, detail: str = None):
        if detail is None:
            if role_id:
                detail = f"Роль с ID {role_id} не найдена"
            elif role_name:
                detail = f"Роль '{role_name}' не найдена"
            else:
                detail = "Роль не найдена"
                
        super().__init__(
            status_code=404,
            error_code="role_not_found",
            detail=detail
        )

class RoleAlreadyExistsException(BaseAPIException):
    """Исключение: роль уже существует"""
    
    def __init__(self, role_name: str = None, detail: str = None):
        if detail is None:
            if role_name:
                detail = f"Роль '{role_name}' уже существует"
            else:
                detail = "Роль уже существует"
                
        super().__init__(
            status_code=409,
            error_code="role_already_exists",
            detail=detail
        )

class RoleValidationException(BaseAPIException):
    """Исключение: ошибка валидации роли"""
    
    def __init__(self, detail: str = None):
        if detail is None:
            detail = "Ошибка валидации данных роли"
            
        super().__init__(
            status_code=400,
            error_code="role_validation_error",
            detail=detail
        )