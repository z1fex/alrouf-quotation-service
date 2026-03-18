"""Application configuration loaded from environment variables.

Uses Pydantic BaseSettings to automatically read from .env file
and environment variables, with sensible defaults for local development.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # When True, uses pre-written templates instead of calling OpenAI API
    USE_MOCK_LLM: bool = True

    # OpenAI API key — only required when USE_MOCK_LLM is False
    OPENAI_API_KEY: Optional[str] = None

    # OpenAI model identifier for email generation
    OPENAI_MODEL: str = "gpt-4o-mini"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


# Singleton settings instance used throughout the application
settings = Settings()
