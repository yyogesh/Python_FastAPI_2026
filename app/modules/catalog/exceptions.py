from app.core.exceptions import BusinessRuleError, ConflictError, NotFoundError


class ProductNotFound(NotFoundError):
    def __init__(self, product_id: int) -> None:
        super().__init__(f"Product {product_id} not found")


class CategoryNotFound(NotFoundError):
    def __init__(self, category_id: int) -> None:
        super().__init__(f"Category {category_id} not found")


class CategoryAlreadyExists(ConflictError):
    def __init__(self, name: str) -> None:
        super().__init__(f"Category '{name}' already exists")


class CategoryHasProducts(ConflictError):
    def __init__(self, category_id: int, count: int) -> None:
        super().__init__(
            f"Category {category_id} still has {count} product(s); move or delete them first"
        )


class PriceBelowCost(BusinessRuleError):
    def __init__(self) -> None:
        super().__init__("price must be higher than cost_price")
