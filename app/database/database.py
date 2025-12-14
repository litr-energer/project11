from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Получаем настройки базы данных из переменных окружения
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./test.db"  # Значение по умолчанию для SQLite
)

# Создаем движок базы данных
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Зависимость для получения сессии базы данных.
    
    Использование:
    ```
    def some_endpoint(db: Session = Depends(get_db)):
        # работа с базой данных через db
        pass
    ```
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Создает все таблицы в базе данных"""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Удаляет все таблицы из базы данных (для тестирования)"""
    Base.metadata.drop_all(bind=engine)