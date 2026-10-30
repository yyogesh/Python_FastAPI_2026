shopapi/
├── app/
│   ├── main.py              # creates the app, includes routers
│   ├── core/                # config, database, security, logging, errors
│   ├── modules/
│   │   ├── catalog/         # models.py, schemas.py, service.py, router.py
│   │   ├── users/
│   │   ├── basket/
│   │   ├── discount/
│   │   ├── ordering/
│   │   └── notification/
│   └── worker.py            # background jobs and outbox processor
├── migrations/              # Alembic
├── tests/
├── docker-compose.yml       # app, postgres, redis, mailpit
└── pyproject.toml


docker compose up -d
up => Create and start every service in docker-compose.yml. Already running services are left alone.
-d => Detached: run in the background and give the terminal back.

docker compose ps  
ps => List the containers with state, health and ports. Wait until both say healthy.

docker compose exec postgres psql -U shop -d shopapi -c "select version();"

docker compose exec redis redis-cli ping


fastapi dev app/main.py
dev : Development mode: auto-reload on save, listens on 127.0.0.1 only.

or 

uvicorn app.main:app --reload


The three rules FastAPI follows, in order:
1. The name appears in the path string, so it is a path parameter.
2. The type is a simple type (int, str, float, bool), so it is a query parameter. A default value makes it optional; no default makes it required.
3. The type is a Pydantic model, so it is read from the JSON body.


from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str = Field(min_length=3)
    price: float = Field(gt=0)
    category: str


p = Product(name="Running shoes", price="2499", category="shoes")
p.price            # 2499.0, the string was converted to a float
p.model_dump()     # {'name': 'Running shoes', 'price': 2499.0, 'category': 'shoes'}

Product(name="ab", price=-5, category="shoes")
# ValidationError: 2 validation errors for Product
#   name: String should have at least 3 characters
#   price: Input should be greater than 0


curl.exe -i -X POST http://127.0.0.1:8000/products -H "Content-Type: application/json" --data "@product.json"


# 1. Raw SQL string, sent with a driver such as asyncpg
rows = await conn.fetch(
    "SELECT id, name, price FROM products WHERE category_id = $1 AND price < $2 ORDER BY price",
    1, 3000,
)

# 2. SQLAlchemy ORM: Python expressions, SQLAlchemy writes the SQL
stmt = (
    select(Product)
    .where(Product.category_id == 1, Product.price < 3000)
    .order_by(Product.price)
)
products = (await db.scalars(stmt)).all()   # a list of Product objects



async def get_db() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        before
        yield session
        end

@router.get("/{product_id}")
async def get_product(product_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    ...

• The code before yield runs before the endpoint; the code after it (here, the end of async with, which closes the session) runs after the response is ready.