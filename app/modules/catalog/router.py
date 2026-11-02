from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.catalog.models import Category, Product
from app.modules.catalog.schemas import (
    CategoryCreate,
    CategoryRead,
    ProductCreate,
    ProductRead,
    ProductUpdate,
)

router = APIRouter(prefix="/products", tags=["catalog"])
category_router = APIRouter(prefix="/categories", tags=["catalog"])

DB = Annotated[AsyncSession, Depends(get_db)]

async def _get_or_404(db: AsyncSession, product_id: int) -> Product:
    product = await db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    return product

async def _check_category(db: AsyncSession, category_id: int) -> None:
    if await db.get(Category, category_id) is None:
        raise HTTPException(status_code=404, detail=f"Category {category_id} not found")

@category_router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(data: CategoryCreate, db: DB):
    category = Category(**data.model_dump())
    db.add(category)
    await db.commit()
    return category

@category_router.get("", response_model=list[CategoryRead])
async def list_categories(db: DB):
    result = await db.scalars(select(Category).order_by(Category.id))
    return result.all()

@router.get("", response_model=list[ProductRead])
async def list_products(
    db: DB,
    category_id: int | None = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    stmt = select(Product).order_by(Product.id).offset(skip).limit(limit)
    if category_id is not None:
        stmt = stmt.where(Product.category_id == category_id)
    result = await db.scalars(stmt)
    return result.all()

@router.get("/{product_id}", response_model=ProductRead)
async def get_product(product_id: Annotated[int, Path(gt=0)], db: DB):
    return await _get_or_404(db, product_id)

@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(data: ProductCreate, db: DB):
    await _check_category(db, data.category_id)
    product = Product(**data.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product

@router.patch("/{product_id}", response_model=ProductRead)
async def update_product(product_id: Annotated[int, Path(gt=0)], data: ProductUpdate, db: DB):
    product = await _get_or_404(db, product_id)
    changes = data.model_dump(exclude_unset=True, exclude_none=True)
    if "category_id" in changes:
        await _check_category(db, changes["category_id"])
    for field, value in changes.items():
        setattr(product, field, value)
    await db.commit()
    await db.refresh(product)
    return product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: Annotated[int, Path(gt=0)], db: DB) -> None:
    product = await _get_or_404(db, product_id)
    await db.delete(product)
    await db.commit()