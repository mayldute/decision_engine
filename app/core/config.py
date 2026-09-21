from pydantic import BaseModel, ConfigDict
from pydantic_settings import BaseSettings


class AppSettings(BaseModel):
    app_name: str
    debug: bool
    env: str


class DatabaseSettings(BaseModel):
    db_login: str
    db_pass: str
    db_host: str
    db_port: str
    db_name: str
    database_url: str
    test_database_url: str


class JwtSettings(BaseModel):
    jwt_secret_key: str
    jwt_algorithm: str
    jwt_access_token_expire_minutes: int
    jwt_refresh_token_expire_days: int


class Settings(BaseSettings):
    app: AppSettings
    database: DatabaseSettings
    jwt: JwtSettings

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )


settings = Settings()
