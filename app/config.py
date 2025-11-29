"""Configuration settings for the Rowboat API SDK Connector."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Rowboat Configuration
    rowboat_host: str
    rowboat_api_key: str
    rowboat_project_id: str

    # Server Configuration
    port: int = 8000
    host: str = "0.0.0.0"
    debug: bool = False

    # OpenWebUI Integration
    enable_owui: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()
