from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False


class DatabaseConfig(BaseModel):
    url: str
    echo: bool = True
    future: bool = True


class AccessTokenConfig(BaseModel):
    lifetime_seconds: int = 3600
    reset_password_token_secret: str = "RESET_PASSWORD_SECRET"
    verification_token_secret: str = "VERIFICATION_SECRET"


class AuthConfig(BaseModel):
    cookie_max_age: int = 3600
    cookie_secure: bool = False
    cookie_samesite: str = "lax"


class UrlPrefix(BaseModel):
    prefix: str = "/api"
    test: str = "/test"
    posts: str = "/posts"
    lab1a1: str = "/lab1"
    auth: str = "/auth"
    users: str = "/users"
    bearer_token_url: str = "/api/auth/login"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.template", ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    run: RunConfig = RunConfig()
    url: UrlPrefix = UrlPrefix()
    db: DatabaseConfig
    access_token: AccessTokenConfig = AccessTokenConfig()
    auth: AuthConfig = AuthConfig()


settings = Settings()
