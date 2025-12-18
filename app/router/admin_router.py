from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.products import ProductModel
from app.models.orders import OrderModel
from app.models.users import UserModel
from app.schemas.product_schema import Product, ProductCreate, ProductUpdate
from app.schemas.order_schema import OrderResponse
from app.repositories.product_repository import ProductRepository
from app.services.product_service import ProductService

router = APIRouter(prefix="/admin", tags=["admin"])


def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    product_repository = ProductRepository(db)
    return ProductService(product_repository)


def check_admin(user_id: int = Query(...), db: Session = Depends(get_db)):
    """Проверить что пользователь админ"""
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    if user.role_id != 2:  # role_id 2 = admin
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user


# ===== ПОЛУЧЕНИЕ ОБЩЕЙ ИНФОРМАЦИИ =====

@router.get("/dashboard")
async def admin_dashboard(
    user_id: int = Query(...),
    admin_user: UserModel = Depends(check_admin),
    db: Session = Depends(get_db)
):
    """
    Получить генеральную информацию для дашборда админа.
    """
    products_count = db.query(ProductModel).count()
    users_count = db.query(UserModel).count()
    admin_count = db.query(UserModel).filter(UserModel.role_id == 2).count()
    
    return {
        "total_products": products_count,
        "total_users": users_count,
        "admin_count": admin_count
    }


# ===== УПРАВЛЕНИЕ ТОВАРАМИ =====

@router.post("/products", response_model=Product)
async def admin_create_product(
    product_data: ProductCreate,
    user_id: int = Query(...),
    admin_user: UserModel = Depends(check_admin),
    db: Session = Depends(get_db),
    product_service: ProductService = Depends(get_product_service)
):
    """
    Создать новый товар (только для админа).
    """
    return product_service.create(product_data.dict())


@router.get("/products", response_model=List[Product])
async def admin_get_products(
    user_id: int = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    admin_user: UserModel = Depends(check_admin),
    product_service: ProductService = Depends(get_product_service)
):
    """
    Получить все товары (только для админа).
    """
    return product_service.get_all(skip, limit)


@router.get("/products/{product_id}", response_model=Product)
async def admin_get_product(
    product_id: int,
    user_id: int = Query(...),
    admin_user: UserModel = Depends(check_admin),
    product_service: ProductService = Depends(get_product_service)
):
    """
    Получить детали товара (только для админа).
    """
    product = product_service.get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product


@router.put("/products/{product_id}", response_model=Product)
async def admin_update_product(
    product_id: int,
    product_data: ProductUpdate,
    user_id: int = Query(...),
    admin_user: UserModel = Depends(check_admin),
    product_service: ProductService = Depends(get_product_service)
):
    """
    Обновить товар (только для админа).
    """
    product = product_service.get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product_service.update(product_id, product_data.dict(exclude_unset=True))


@router.delete("/products/{product_id}")
async def admin_delete_product(
    product_id: int,
    user_id: int = Query(...),
    admin_user: UserModel = Depends(check_admin),
    product_service: ProductService = Depends(get_product_service)
):
    """
    Удалить товар (только для админа).
    """
    success = product_service.delete(product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return {"message": "Product deleted successfully"}


# ===== УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ =====

@router.get("/users", response_model=List[dict])
async def admin_get_users(
    user_id: int = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    admin_user: UserModel = Depends(check_admin),
    db: Session = Depends(get_db)
):
    """
    Получить всех пользователей (только для админа).
    """
    users = db.query(UserModel).offset(skip).limit(limit).all()
    
    return [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role_id": user.role_id,
            "role_name": user.role.name if user.role else "Unknown"
        }
        for user in users
    ]


@router.get("/users/{user_id_param}", response_model=dict)
async def admin_get_user(
    user_id_param: int,
    user_id: int = Query(...),
    admin_user: UserModel = Depends(check_admin),
    db: Session = Depends(get_db)
):
    """
    Получить детали пользователя (только для админа).
    """
    user = db.query(UserModel).filter(UserModel.id == user_id_param).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role_id": user.role_id,
        "role_name": user.role.name if user.role else "Unknown"
    }


@router.delete("/users/{user_id_param}")
async def admin_delete_user(
    user_id_param: int,
    user_id: int = Query(...),
    admin_user: UserModel = Depends(check_admin),
    db: Session = Depends(get_db)
):
    """
    Удалить пользователя (только для админа).
    """
    user = db.query(UserModel).filter(UserModel.id == user_id_param).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.delete(user)
    db.commit()
    
    return {"message": f"User {user.name} deleted successfully"}
