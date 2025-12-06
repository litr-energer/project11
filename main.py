import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
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
async def read_page4(request: Request):
    return templates.TemplateResponse("favorite.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run(app=app)