import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    DB_NAME: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_DEBUG: bool = True
    
    # Email (Optional)
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # Admin
    ADMIN_USER_ID: Optional[int] = None
    ADMIN_EMAIL: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"),
        env_file_encoding="utf-8",
        extra="ignore"  # Разрешаем лишние поля в .env
    )
    
    @property
    def get_db_url(self):
        # Если используете SQLite через SQLAlchemy
        if self.DATABASE_URL.startswith("sqlite://"):
            # Преобразуем формат для SQLAlchemy
            return f"sqlite+aiosqlite:///{self.DATABASE_URL.replace('sqlite:///', '')}"
        return self.DATABASE_URL

    @property
    def auth_data(self):
        return {"secret_key": self.SECRET_KEY, "algorithm": self.ALGORITHM}


settings = Settings()