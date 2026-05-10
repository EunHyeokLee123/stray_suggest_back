from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Gateway Monolith API"
    api_prefix: str = "/api"

    # DB
    db_host: str
    db_port: int
    db_user: str | None = None
    db_password: str | None = None
    db_name: str

    # API Keys
    openai_api_key: str | None = None
    gemini_api_key: str | None = None

    # App
    app_name: str = "My Backend"
    api_prefix: str = "/api"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()