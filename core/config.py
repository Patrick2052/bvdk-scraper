from typing import Any, Callable, Set, Annotated
from pprint import pformat
import shutil
from urllib.parse import quote_plus
from datetime import timedelta
from pydantic import (
    # AliasChoices,
    # AmqpDsn,
    # BaseModel,
    StringConstraints,
    Field,
    IPvAnyAddress,
    AnyHttpUrl,
    # ImportString,
    PostgresDsn,
    EmailStr,
    AnyUrl
)

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App configuration"""

    model_config = SettingsConfigDict(env_file='.env',
                                      env_file_encoding='utf-8')

    app_name: str = "BVDK Website Scraper for Comps"

    # postgres_dsn: PostgresDsn = Field(alias="POSTGRES_DSN")
    postgres_username: str
    postgres_password: str
    postgres_host: AnyHttpUrl | IPvAnyAddress
    postgres_database: str

    echo_sql: bool = True

    # email
    smtp_server: str | IPvAnyAddress
    smtp_port: int = 587
    smtp_use_tls: bool = True
    email_address: EmailStr
    email_password: str

    # this isnt parsed from env

    @property
    def postgres_dsn(self) -> PostgresDsn:
        password = quote_plus(self.postgres_password)
        return f"postgresql://{self.postgres_username}:{password}@{self.postgres_host}/{self.postgres_database}"  # noqa

    # prevent sensetive cred from being printed

    def model_dump(self, *args, **kwargs):
        d = super().model_dump(*args, **kwargs)
        censored_keys = [
            "postgres_password",
            "email_password"
        ]
        for key in censored_keys:
            if key in d:
                d[key] = '******'
        return d


settings = Settings()
