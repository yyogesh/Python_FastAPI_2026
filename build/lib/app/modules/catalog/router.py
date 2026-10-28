import datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, status

from app.modules.catalog.schemas import ProductCreate, ProductRead, ProductUpdate


router  = APIRouter(prefix="/products", tags=["catalog"])

_products: dict[int, dict[str, str]] = {}

_next_id = 1


@router.get("", response_model= list[ProductRead])
async def list_products(
    category: str | None = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20
):
    items = list(_products.values())
    if category is not None:
        items = [item for item in items if item["category"] == category]
        # [2:4] => 2,3
    return items[skip : skip + limit]


@router.get("/{product_id}", response_model= list[ProductRead])
async def get_product(product_id: Annotated[int, Query(gt=0)]):
    return _get_or_404(product_id)


def _get_or_404(product_id: int) -> dict[str, str]:
    if product_id not in _products:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    return _products[product_id]


@router.post("", response_model=ProductRead, status_code= status.HTTP_201_CREATED)
async def create_product(data: ProductCreate):
    global _next_id
    product = {
        "id": _next_id,
        "created_at": datetime.now(datetime.timezone.utc),
        **data.model_dump(),
    }
    _products[_next_id] = product
    _next_id += 1
    return product


@router.patch("/{product_id}", response_model=ProductRead)
async def update_product(product_id: Annotated[int, Path(gt=0)], data: ProductUpdate):
    product = _get_or_404(product_id)
    product.update(data.model_dump(exclude_unset=True, exclude_none=True))
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: Annotated[int, Path(gt=0)]) -> None:
    _get_or_404(product_id)
    del _products[product_id]