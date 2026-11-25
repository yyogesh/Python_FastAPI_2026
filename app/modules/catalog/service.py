from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.catalog.exceptions import (
    CategoryAlreadyExists,
    CategoryHasProducts,
    CategoryNotFound,
    PriceBelowCost,
    ProductNotFound,
)
from app.modules.catalog.models import Category, Product
from app.modules.catalog.schemas import (
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
    ProductCreate,
    ProductRead,
    ProductUpdate,
)


# ---------- private helpers ----------

async def _get_product(db: AsyncSession, product_id: int) -> Product:
    product = await db.get(Product, product_id)
    if product is None:
        raise ProductNotFound(product_id)
    return product


async def _get_category(db: AsyncSession, category_id: int) -> Category:
    category = await db.get(Category, category_id)
    if category is None:
        raise CategoryNotFound(category_id)
    return category


async def _ensure_category_name_free(
    db: AsyncSession, name: str, exclude_id: int | None = None
) -> None:
    stmt = select(Category.id).where(Category.name == name)
    if exclude_id is not None:
        stmt = stmt.where(Category.id != exclude_id)
    if await db.scalar(stmt) is not None:
        raise CategoryAlreadyExists(name)


async def _commit_category(db: AsyncSession, name: str) -> None:
    # The name check above can lose a race; the unique constraint is the final word.
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise CategoryAlreadyExists(name)


def _check_price(price: Decimal | float, cost_price: Decimal | float | None) -> None:
    if cost_price is not None and price <= cost_price:
        raise PriceBelowCost()


# ---------- categories ----------

async def list_categories(db: AsyncSession) -> list[CategoryRead]:
    categories = await db.scalars(select(Category).order_by(Category.id))
    return [CategoryRead.model_validate(c) for c in categories]


async def get_category(db: AsyncSession, category_id: int) -> CategoryRead:
    return CategoryRead.model_validate(await _get_category(db, category_id))


async def create_category(db: AsyncSession, data: CategoryCreate) -> CategoryRead:
    await _ensure_category_name_free(db, data.name)
    category = Category(**data.model_dump())
    db.add(category)
    await _commit_category(db, data.name)
    return CategoryRead.model_validate(category)


async def update_category(
    db: AsyncSession, category_id: int, data: CategoryUpdate
) -> CategoryRead:
    category = await _get_category(db, category_id)
    changes = data.model_dump(exclude_unset=True, exclude_none=True)
    if "name" in changes:
        await _ensure_category_name_free(db, changes["name"], exclude_id=category_id)
        category.name = changes["name"]
        await _commit_category(db, changes["name"])
    return CategoryRead.model_validate(category)


async def delete_category(db: AsyncSession, category_id: int) -> None:
    category = await _get_category(db, category_id)
    count = await db.scalar(
        select(func.count()).select_from(Product).where(Product.category_id == category_id)
    ) or 0
    if count > 0:
        raise CategoryHasProducts(category_id, count)
    await db.delete(category)
    await db.commit()


# ---------- products ----------

async def list_products(
    db: AsyncSession, category_id: int | None, skip: int, limit: int
) -> list[ProductRead]:
    stmt = select(Product).order_by(Product.id).offset(skip).limit(limit)
    if category_id is not None:
        stmt = stmt.where(Product.category_id == category_id)
    products = await db.scalars(stmt)
    return [ProductRead.model_validate(p) for p in products]


async def get_product(db: AsyncSession, product_id: int) -> ProductRead:
    return ProductRead.model_validate(await _get_product(db, product_id))


async def create_product(db: AsyncSession, data: ProductCreate) -> ProductRead:
    await _get_category(db, data.category_id)
    _check_price(data.price, data.cost_price)
    product = Product(**data.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return ProductRead.model_validate(product)


async def update_product(
    db: AsyncSession, product_id: int, data: ProductUpdate
) -> ProductRead:
    product = await _get_product(db, product_id)
    changes = data.model_dump(exclude_unset=True, exclude_none=True)
    if "category_id" in changes:
        await _get_category(db, changes["category_id"])
    _check_price(
        changes.get("price", product.price),
        changes.get("cost_price", product.cost_price),
    )
    for field, value in changes.items():
        setattr(product, field, value)
    await db.commit()
    await db.refresh(product)
    return ProductRead.model_validate(product)


async def delete_product(db: AsyncSession, product_id: int) -> None:
    product = await _get_product(db, product_id)
    await db.delete(product)
    await db.commit()
