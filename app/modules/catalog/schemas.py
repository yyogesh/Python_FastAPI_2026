from datetime import datetime

from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    price: float = Field(gt=0)
    category: str = Field(min_length=2, max_length=50)


class ProductCreate(ProductBase):
    cost_price: float | None = Field(default=None, gt=0)


class ProductUpdate(BaseModel):
    cost_price: float | None = Field(default=None, gt=0)


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    price: float | None = Field(default=None, gt=0)
    category: str | None = Field(default=None, min_length=2, max_length=50)
    cost_price: float | None = Field(default=None, gt=0)


class ProductRead(ProductBase):
    id: int
    created_at: datetime