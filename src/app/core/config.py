from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

class Setting(BaseSettings):
    """
    Application settings loaded from environment variables or .env file.
    """

    app_name: str = "agent-api"
    app_env: str = "dev"

    llm_provider: Literal["mock", "ollama"] = "mock"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:7b"
    ollama_temperature: float = 0.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

@lru_cache
def get_settings() -> Setting:
    return Setting()