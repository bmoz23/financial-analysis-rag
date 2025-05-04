# shared/db.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from pydantic_settings import BaseSettings
from pydantic import Field

class _DBSettings(BaseSettings):
    postgres_uri: str = Field(..., alias="POSTGRES_URI")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }

_settings = _DBSettings()

engine = create_async_engine(_settings.postgres_uri, echo=False)
AsyncSession = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()
