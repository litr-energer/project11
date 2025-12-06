from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.database.database import get_async_session
from app.models.products import ProductModel
from app.schemes.products import ProductCreate, ProductUpdate, ProductResponse

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


@router.get("/", response_model=List[ProductResponse])
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить список продуктов с пагинацией и фильтрацией
    """
    query = select(ProductModel)
    
    if category:
        query = query.where(ProductModel.category == category)
    
    if is_active is not None:
        query = query.where(ProductModel.is_active == is_active)
    
    query = query.offset(skip).limit(limit)
    
    result = await session.execute(query)
    products = result.scalars().all()
    return products


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить продукт по ID
    """
    query = select(ProductModel).where(ProductModel.id == product_id)
    result = await session.execute(query)
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Создать новый продукт
    """
    # Проверяем, есть ли продукт с таким названием
    query = select(ProductModel).where(ProductModel.title == product_data.title)
    result = await session.execute(query)
    existing_product = result.scalar_one_or_none()
    
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this title already exists"
        )
    
    # Создаем новый продукт
    db_product = ProductModel(**product_data.dict())
    session.add(db_product)
    await session.commit()
    await session.refresh(db_product)
    
    return db_product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Обновить продукт
    """
    # Проверяем существование продукта
    query = select(ProductModel).where(ProductModel.id == product_id)
    result = await session.execute(query)
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Обновляем продукт
    update_data = product_data.dict(exclude_unset=True)
    if update_data:
        stmt = (
            update(ProductModel)
            .where(ProductModel.id == product_id)
            .values(**update_data)
        )
        await session.execute(stmt)
        await session.commit()
        
        # Получаем обновленный продукт
        result = await session.execute(select(ProductModel).where(ProductModel.id == product_id))
        product = result.scalar_one()
    
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Удалить продукт (мягкое удаление - установка is_active=False)
    """
    query = select(ProductModel).where(ProductModel.id == product_id)
    result = await session.execute(query)
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Мягкое удаление
    stmt = (
        update(ProductModel)
        .where(ProductModel.id == product_id)
        .values(is_active=False)
    )
    await session.execute(stmt)
    await session.commit()


@router.get("/category/{category_name}", response_model=List[ProductResponse])
async def get_products_by_category(
    category_name: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить продукты по категории
    """
    query = (
        select(ProductModel)
        .where(ProductModel.category == category_name)
        .where(ProductModel.is_active == True)
        .offset(skip)
        .limit(limit)
    )
    
    result = await session.execute(query)
    products = result.scalars().all()
    return products


@router.post("/{product_id}/increment-popularity")
async def increment_popularity(
    product_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Увеличить счетчик популярности продукта
    """
    query = select(ProductModel).where(ProductModel.id == product_id)
    result = await session.execute(query)
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    stmt = (
        update(ProductModel)
        .where(ProductModel.id == product_id)
        .values(popularity=ProductModel.popularity + 1)
    )
    await session.execute(stmt)
    await session.commit()
    
    return {"message": "Popularity incremented"}