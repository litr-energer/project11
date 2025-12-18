from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.users import UserModel


# Зависимость для получения текущего пользователя из заголовка
def get_current_user(user_id: int = None, db: Session = Depends(get_db)) -> UserModel:
    """
    Получает текущего пользователя. 
    В реальной системе нужно получать из JWT токена.
    Пока для тестирования передаем user_id в запросе.
    """
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID required"
        )
    
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


def require_admin(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    """
    Зависимость для проверки, что пользователь - администратор.
    Используется для защиты админ-маршрутов.
    """
    if current_user.role.name.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_user(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    """
    Зависимость для проверки, что пользователь авторизован (любая роль).
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return current_user
