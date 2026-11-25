Create a CLAUDE.md file in the project root for ShopAPI, a FastAPI e-commerce backend we are building in a 20-day course.

Include these sections:
- Stack: Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2.0 async with asyncpg, Alembic, PostgreSQL in Docker Compose. Learners use Windows and PowerShell.
- Layout: app/core for shared pieces; app/modules/<module>/ with models.py, schemas.py, service.py, router.py.
- Rules:
  - Routers speak HTTP only: read the request, call one service function, return its result. No queries, no business rules, no try/except.
  - Services hold the business rules. They never import FastAPI, never raise HTTPException, never use status codes.
  - Services raise domain exceptions (NotFoundError, ConflictError, BusinessRuleError from app/core/exceptions.py, or module subclasses). One handler in app/core/errors.py maps them to 404 / 409 / 400.
  - Public service functions return Pydantic Read schemas, never SQLAlchemy models. Private helpers start with an underscore.
  - Other modules use a module only through its service.py.
  - Pydantic v2 and SQLAlchemy 2.0 style only.
  - Every schema change is an Alembic migration; always name constraints explicitly.
  - Never run alembic upgrade or downgrade, git commit, or anything that deletes data unless I ask. Show me the command instead.
- Commands: how to run the app and create a migration.

Keep it short: plain bullet points, no explanations of FastAPI itself.



Create app/core/exceptions.py with the base exceptions every ShopAPI module will use to signal a business rule failure.

- DomainError(Exception): takes a message string, passes it to Exception, and keeps it as self.message.
- Three subclasses with a one-line docstring each and no other body: NotFoundError (the thing does not exist), ConflictError (clashes with existing data), BusinessRuleError (well-formed request that breaks a rule).

No FastAPI imports and no status codes in this file. Do not change any other file.



Create app/core/errors.py with one FastAPI exception handler for DomainError from app/core/exceptions.py.

- Keep a single dict STATUS_CODES that maps NotFoundError to 404, ConflictError to 409 and BusinessRuleError to 400. This dict must be the only place in the project that links an error type to a status code.
- The handler picks the code with isinstance, so subclasses match their parent. A plain DomainError gets 400.
- Respond with JSONResponse and the body {"detail": exc.message}, the same shape HTTPException uses.
- Expose register_exception_handlers(app) that registers the handler for DomainError.

Then call register_exception_handlers(app) in app/main.py right after the app is created. Change nothing else in main.py.



Create app/modules/catalog/exceptions.py with the Catalog's own domain exceptions, built on app/core/exceptions.py. Each takes the facts as arguments and builds its own message:

- ProductNotFound(product_id) -> NotFoundError, "Product {id} not found"
- CategoryNotFound(category_id) -> NotFoundError, "Category {id} not found"
- CategoryAlreadyExists(name) -> ConflictError, "Category '{name}' already exists"
- CategoryHasProducts(category_id, count) -> ConflictError, "Category {id} still has {count} product(s); move or delete them first"
- PriceBelowCost() -> BusinessRuleError, "price must be higher than cost_price"

Also add a CategoryUpdate schema to app/modules/catalog/schemas.py, below CategoryCreate: name is optional, with the same length limits as CategoryCreate. Do not change the existing schemas.




Move all Catalog business logic from app/modules/catalog/router.py into app/modules/catalog/service.py, which is empty today. Do not change router.py yet; that is the next step.

What the service must contain:
- Private helpers: _get_product and _get_category (load by id or raise ProductNotFound / CategoryNotFound), _ensure_category_name_free(db, name, exclude_id=None) that raises CategoryAlreadyExists, and _check_price(price, cost_price) that raises PriceBelowCost when cost_price is set and price <= cost_price.
- Categories: list_categories, get_category, create_category, update_category, delete_category.
- Products: list_products (category_id filter, skip, limit, ordered by id), get_product, create_product, update_product, delete_product.

Rules:
- Every function takes db: AsyncSession as its first argument. Full type hints.
- Public functions return CategoryRead / ProductRead (or lists of them) via model_validate, never models.
- Creating or renaming a category checks the name first; also catch IntegrityError on commit, roll back, and raise CategoryAlreadyExists, in case two requests race.
- delete_category raises CategoryHasProducts with the count if the category still has products.
- create_product and update_product check the category exists and apply _check_price. On update, use the stored price or cost_price for whichever the client did not send.
- No FastAPI imports, no HTTPException, no status codes.

Show me the plan first: the list of functions with one line each on what they check and raise.




Rewrite app/modules/catalog/router.py so every endpoint is a thin wrapper around app/modules/catalog/service.py.

- Each endpoint body is one line: return await service.<function>(...) (or await without return for deletes).
- Keep every existing URL, response_model and success status code exactly as they are today.
- Add GET, PATCH and DELETE for /categories/{category_id}, using CategoryUpdate for PATCH and 204 for DELETE.
- Path ids use Annotated[int, Path(gt=0)] through two aliases, ProductId and CategoryId, like the DB alias.
- Import the service module (from app.modules.catalog import service), not individual functions.
- No HTTPException, no select, no models, no try/except in the router.