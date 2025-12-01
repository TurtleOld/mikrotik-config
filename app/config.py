from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = 'development'
    mikrotik_default_port: int = 80
    mikrotik_timeout: int = 10
    mikrotik_username: str
    mikrotik_password: str

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
    )


settings = Settings()

