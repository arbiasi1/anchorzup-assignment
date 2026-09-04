from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://content_filter:content_filter@localhost:5432/content_filter"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

