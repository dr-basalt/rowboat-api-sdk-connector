"""Configuration settings for the Rowboat API SDK Connector."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Rowboat Configuration (Optional - can be provided per request)
    rowboat_host: Optional[str] = None
    rowboat_api_key: Optional[str] = None
    rowboat_project_id: Optional[str] = None

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
        # Don't fail if .env file doesn't exist
        env_file_required = False
        extra = "ignore"


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()
