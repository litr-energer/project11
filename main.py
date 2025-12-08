import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
from pathlib import Path
import os

# Импортируйте ваши роутеры
from app.api.sample import router as sample_router
from app.api.auth import router as auth_router
from app.api.roles import router as role_router
from app.api.products import router as products_router
from app.api.favorites import router as favorites_router
from app.api.chat_massage import router as chat_router 
from app.api.cart import router as cart_router  
from app.api.cart_items import router as cart_items_router
from app.api.orders import router as orders_router
from app.api.listing import router as listing_router
from app.api.author_listing import router as author_listing_router
from app.api.review import router as review_router

app = FastAPI(title="individual_project_template", version="0.0.1")

# Добавляем CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене измените на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Определите пути
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = os.path.join(BASE_DIR, "app", "templates")
STATIC_DIR = os.path.join(BASE_DIR, "app", "static")

# Подключите статические файлы (CSS, JS, изображения)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Настройте шаблоны
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Включите ваши API роутеры
app.include_router(sample_router)
app.include_router(auth_router)
app.include_router(role_router)
app.include_router(products_router)
app.include_router(favorites_router)
app.include_router(chat_router)
app.include_router(cart_items_router)
app.include_router(cart_router)
app.include_router(orders_router)
app.include_router(listing_router)
app.include_router(author_listing_router)
app.include_router(review_router)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "API is running"}

@app.get("/api/info")
async def api_info():
    return {
        "name": "individual_project_template",
        "version": "0.0.1",
        "status": "running"
    }

# Тестовый endpoint
@app.get("/api/test")
async def test_endpoint():
    return {"message": "API is working"}

# Базовый products endpoint для совместимости с фронтендом
@app.get("/api/products/")
async def get_products(limit: int = 20, offset: int = 0):
    return []

# Создайте маршруты для ваших HTML страниц
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/cart.html", response_class=HTMLResponse)
async def read_page1(request: Request):
    return templates.TemplateResponse("cart.html", {"request": request})

@app.get("/auth.html", response_class=HTMLResponse)
async def read_page2(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})

# Добавьте маршруты для остальных 3 HTML файлов
@app.get("/account.html", response_class=HTMLResponse)
async def read_page3(request: Request):
    return templates.TemplateResponse("account.html", {"request": request})

@app.get("/chat.html", response_class=HTMLResponse)
async def read_page4(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/favorite.html", response_class=HTMLResponse)
async def read_favorite(request: Request):
    return templates.TemplateResponse("favorite.html", {"request": request})

# 404 страница
@app.get("/404.html", response_class=HTMLResponse)
async def not_found_page(request: Request):
    return templates.TemplateResponse("404.html", {"request": request})

# Favicon
@app.get("/favicon.ico")
async def favicon():
    favicon_path = os.path.join(STATIC_DIR, "favicon.ico")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    return JSONResponse(status_code=404, content={"detail": "Favicon not found"})

# Обработчик 404 ошибок
@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: HTTPException):
    if request.url.path.endswith('.html'):
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    return JSONResponse(
        status_code=404,
        content={"detail": "Not Found"}
    )

if __name__ == "__main__":
    uvicorn.run(
        app=app,
        host="0.0.0.0",
        port=8000,
    )