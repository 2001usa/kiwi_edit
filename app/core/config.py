from pydantic_settings import BaseSettings
from pydantic import Field, BeforeValidator
from typing import List, Any
from typing_extensions import Annotated
import json

def parse_list(v: Any) -> List[int]:
    if isinstance(v, list):
        return [int(x) for x in v]
    if isinstance(v, str):
        v = v.strip()
        if not v:
            return []
        if v.startswith("[") and v.endswith("]"):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                pass
        return [int(x) for x in v.split(",") if x.strip()]
    if isinstance(v, int):
        return [v]
    return v

class Settings(BaseSettings):
    BOT_TOKEN: str
    BOT_USERNAME: str = "media_bot"
    ADS_MANAGER_USERNAME: str = "aslbek_1203"
    SENTRY_DSN: str = "" # Optional
    
    # Database
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "media_bot"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    
    # Railway provides DATABASE_URL directly
    DATABASE_URL_VAL: str = Field(default="", alias="DATABASE_URL")
    
    @property
    def DATABASE_URL(self) -> str:
        # Check if DATABASE_URL is provided (Railway style)
        if self.DATABASE_URL_VAL:
            # Ensure it starts with postgresql+asyncpg://
            url = self.DATABASE_URL_VAL
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif url.startswith("postgresql://") and "asyncpg" not in url:
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return url
            
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # Railway provides REDIS_URL directly
    REDIS_URL_VAL: str = Field(default="", alias="REDIS_URL")

    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_URL_VAL:
             return self.REDIS_URL_VAL
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    # Telegram Channels
    TRAILERS_BASE_CHAT: int
    SERIES_BASE_CHAT: int
    
    # Validation for ADMIN_IDS
    ADMIN_IDS: Annotated[List[int], BeforeValidator(parse_list)] = []
    
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]


    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = "ignore" # Ignore extra fields (like REDIS_URL if not defined in model but present in env)

settings = Settings()
