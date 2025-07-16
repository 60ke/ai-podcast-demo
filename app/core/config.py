import os
from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Dict, Any

class Settings(BaseSettings):
    # MySQL配置
    MYSQL_HOST: str = Field(default="localhost")
    MYSQL_PORT: int = Field(default=3306)
    MYSQL_USER: str = Field(default="root")
    MYSQL_PASSWORD: str = Field(default="password")
    MYSQL_DB: str = Field(default="podcast")

    # LLM服务商配置（可扩展）
    LLM_PROVIDERS: Dict[str, Any] = Field(default_factory=lambda: {
        "openai": {
            "api_key": os.getenv("OPENAI_API_KEY", ""),
            "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        }
    })

    JWT_SECRET_KEY: str = Field(default="your-secret-key")
    JWT_ALGORITHM: str = Field(default="HS256")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
