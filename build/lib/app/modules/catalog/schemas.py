import datetime

from pydantic import BaseModel

class ProductBase(BaseModel):
    name: str
    description: str | None = None
    price: float
    category: str


class ProductCreate(ProductBase):
    cost_price: float | None = None


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    category: str | None = None
    cost_price: float | None = None

class ProductRead(ProductBase):
    id: int
    created_at: datetime