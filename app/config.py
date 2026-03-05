"""Application configuration with intentional security vulnerabilities."""

import os

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    app_name: str = "Notes API"
    lab_mode: bool = False


    secret_key: str = Field(
        default="test-secret-key-min-32-chars-long-for-testing",
        min_length=32
    )
    api_token: str = Field(
        default="test-api-token-20chars-min",
        min_length=20
    )

    class Config:
        env_file = ".env"
        case_sensitive = False
        env_prefix = "APP_"



def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings(
        lab_mode=os.getenv("LAB_MODE", "0") == "1"
    )
