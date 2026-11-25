from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.catalog import service
from app.modules.catalog.schemas import (
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
    ProductCreate,
    ProductRead,
    ProductUpdate,
)

router = APIRouter(prefix="/products", tags=["catalog"])
category_router = APIRouter(prefix="/categories", tags=["catalog"])

DB = Annotated[AsyncSession, Depends(get_db)]
ProductId = Annotated[int, Path(gt=0)]
CategoryId = Annotated[int, Path(gt=0)]


# ---------- categories ----------

@category_router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(data: CategoryCreate, db: DB):
    return await service.create_category(db, data)


@category_router.get("", response_model=list[CategoryRead])
async def list_categories(db: DB):
    return await service.list_categories(db)


@category_router.get("/{category_id}", response_model=CategoryRead)
async def get_category(category_id: CategoryId, db: DB):
    return await service.get_category(db, category_id)


@category_router.patch("/{category_id}", response_model=CategoryRead)
async def update_category(category_id: CategoryId, data: CategoryUpdate, db: DB):
    return await service.update_category(db, category_id, data)


@category_router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: CategoryId, db: DB) -> None:
    await service.delete_category(db, category_id)


# ---------- products ----------

@router.get("", response_model=list[ProductRead])
async def list_products(
    db: DB,
    category_id: int | None = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return await service.list_products(db, category_id, skip, limit)


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(product_id: ProductId, db: DB):
    return await service.get_product(db, product_id)


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(data: ProductCreate, db: DB):
    return await service.create_product(db, data)


@router.patch("/{product_id}", response_model=ProductRead)
async def update_product(product_id: ProductId, data: ProductUpdate, db: DB):
    return await service.update_product(db, product_id, data)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: ProductId, db: DB) -> None:
    await service.delete_product(db, product_id)
