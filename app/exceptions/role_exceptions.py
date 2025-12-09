from .base_exceptions import NotFoundException, ConflictException, ValidationException


class RoleNotFoundException(NotFoundException):
    """Исключение, когда роль не найдена"""
    
    def __init__(self, role_id: int = None, role_name: str = None):
        if role_id:
            super().__init__(resource_name="Role", resource_id=role_id)
        elif role_name:
            detail = f"Role with name '{role_name}' not found"
            super().__init__(
                status_code=404,
                detail=detail,
                error_code="ROLE_NOT_FOUND",
                extra={"role_name": role_name}
            )
        else:
            super().__init__(resource_name="Role", resource_id="unknown")


class RoleAlreadyExistsException(ConflictException):
    """Исключение, когда роль с таким именем уже существует"""
    
    def __init__(self, role_name: str):
        detail = f"Role with name '{role_name}' already exists"
        super().__init__(
            detail=detail,
            error_code="ROLE_ALREADY_EXISTS",
            extra={"role_name": role_name}
        )


class RoleValidationException(ValidationException):
    """Исключение для ошибок валидации роли"""
    
    def __init__(self, detail: str = "Role validation error", errors: list = None):
        super().__init__(detail=detail, errors=errors, error_code="ROLE_VALIDATION_ERROR")