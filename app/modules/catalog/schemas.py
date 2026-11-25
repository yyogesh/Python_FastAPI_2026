from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=50)


class CategoryRead(CategoryCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class ProductBase(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    price: float = Field(gt=0)
    stock: int = Field(default=0, ge=0)
    category_id: int = Field(gt=0)


class ProductCreate(ProductBase):
    cost_price: float | None = Field(default=None, gt=0)


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    price: float | None = Field(default=None, gt=0)
    stock: int | None = Field(default=None, ge=0)
    category_id: int | None = Field(default=None, gt=0)
    cost_price: float | None = Field(default=None, gt=0)


class ProductRead(ProductBase):
    model_config = ConfigDict(from_attributes=True)
    # Let Pydantic read values from object attributes (product.name), not only from dict keys (product["name"]).
    #  response_model already does this for objects we return,
    #  but ProductRead.model_validate(product) in our own code fails without it

    id: int
    created_at: datetime