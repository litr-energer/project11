from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.database import engine, Base, create_tables
# Импорт из router (в единственном числе)
from app.router import (
    role_router,
    user_router,
    product_router,
    listing_router,
    author_listing_router,
    order_router,
    cart_router,
    favorite_router,
    review_router,
    chat_message_router
)
from app.exceptions.handler import setup_exception_handlers
import logging
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan менеджер для управления событиями запуска и остановки приложения.
    """
    # События при запуске
    logger.info("🚀 Starting E-Commerce API...")
    
    # Создание таблиц в базе данных
    try:
        create_tables()
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        raise
    
    logger.info(f"📊 Database URL: {os.getenv('DATABASE_URL', 'sqlite:///./app.db')}")
    logger.info("✅ Application started successfully")
    
    yield  # Здесь приложение работает
    
    # События при остановке
    logger.info("🛑 Shutting down E-Commerce API...")
    logger.info("👋 Application stopped successfully")


# Создание приложения FastAPI
app = FastAPI(
    title="E-Commerce API",
    description="API для интернет-магазина с системой авторов и листингов",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройка обработчиков исключений
setup_exception_handlers(app)

# Подключение всех роутеров
app.include_router(role_router.router)
app.include_router(user_router.router)
app.include_router(product_router.router)
app.include_router(listing_router.router)
app.include_router(author_listing_router.router)
app.include_router(order_router.router)
app.include_router(cart_router.router)
app.include_router(favorite_router.router)
app.include_router(review_router.router)
app.include_router(chat_message_router.router)


@app.get("/")
def read_root():
    return {
        "message": "Добро пожаловать в E-Commerce API",
        "documentation": "/docs",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )