from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.product_service import ProductService
from app.repositories.product_repository import ProductRepository
from app.schemas.product_schema import Product, ProductCreate, ProductUpdate
from app.services.product_service import ProductService
from app.repositories.product_repository import ProductRepository

router = APIRouter(prefix="/products", tags=["products"])

def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    product_repository = ProductRepository(db)
    return ProductService(product_repository)

router = APIRouter(prefix="/products", tags=["products"])

def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    product_repository = ProductRepository(db)
    return ProductService(product_repository)

@router.get("/", response_model=List[Product])
def get_products(
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    active_only: bool = True,
    product_service: ProductService = Depends(get_product_service)
):
    if category:
        return product_service.get_by_category(category, skip, limit)
    elif active_only:
        return product_service.get_active_products(skip, limit)
    else:
        return product_service.get_all(skip, limit)

@router.get("/{product_id}", response_model=Product)
def get_product(
    product_id: int,
    product_service: ProductService = Depends(get_product_service)
):
    product = product_service.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/", response_model=Product)
def create_product(
    product_data: ProductCreate,
    product_service: ProductService = Depends(get_product_service)
):
    return product_service.create(product_data.dict())

@router.put("/{product_id}", response_model=Product)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    product_service: ProductService = Depends(get_product_service)
):
    product = product_service.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product_service.update(product_id, product_data.dict(exclude_unset=True))

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    product_service: ProductService = Depends(get_product_service)
):
    success = product_service.delete(product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

@router.patch("/{product_id}/activate")
def activate_product(
    product_id: int,
    product_service: ProductService = Depends(get_product_service)
):
    product = product_service.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # ИСПРАВЛЕНО: is_acctive → is_active
    product_service.update(product_id, {"is_active": True})
    return {"message": "Product activated successfully"}

@router.patch("/{product_id}/deactivate")
def deactivate_product(
    product_id: int,
    product_service: ProductService = Depends(get_product_service)
):
    product = product_service.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # ИСПРАВЛЕНО: is_acctive → is_active
    product_service.update(product_id, {"is_active": False})
    return {"message": "Product deactivated successfully"}