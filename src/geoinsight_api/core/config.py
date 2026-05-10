from functools import cached_property

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_host: str = Field(alias="DATABASE_HOST")
    database_port: str = Field(alias="DATABASE_PORT")
    database_name: str = Field(alias="DATABASE_NAME")
    database_user: str = Field(alias="DATABASE_USER")
    database_password: str = Field(alias="DATABASE_PASSWORD")
    database_echo: bool = Field(alias="DATABASE_ECHO")

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    @cached_property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.database_user}:"
            f"{self.database_password}@"
            f"{self.database_host}:"
            f"{self.database_port}/"
            f"{self.database_name}"
        )


settings = Settings()
