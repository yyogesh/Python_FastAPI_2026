from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file = ".env", extra="ignore")

    app_name: str= "shopapi"
    app_version: str= "0.1.0"
    app_description: str= "E-commerce backend built in FastAPI in 20 days"
    app_docs_url: str= "/docs"
    app_redoc_url: str= "/redoc"
    app_openapi_url: str= "/openapi.json"
    app_contact_name: str= "Ruslan"
    enviroment: str = "local"

settings = Settings()