from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class YandexConfig(BaseSettings):
    client_id: str
    client_secret: SecretStr

    model_config = SettingsConfigDict(
        env_prefix="YNDX_",
        env_file=".env",
        env_file_encoding="utf-8",
    )
