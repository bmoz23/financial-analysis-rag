# ingestion/config.py

from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    twelve_api_key: str = Field(..., alias="TWELVE_API_KEY")
    symbols_raw: str = Field("AAPL,MSFT", alias="SYMBOLS")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }

    @property
    def symbols(self) -> list[str]:
        return [s.strip() for s in self.symbols_raw.split(",") if s.strip()]

settings = Settings()
