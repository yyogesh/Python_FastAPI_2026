from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file = ".env", extra="ignore")

    app_name: str = "ShopAPI"
    app_version: str = "0.1.0"
    environment: str = "local"
    database_url: str = "postgresql+asyncpg://shop:shop@localhost:5432/shopapi"
    db_echo: bool = False

settings = Settings()