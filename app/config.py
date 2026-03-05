"""Application configuration with intentional security vulnerabilities."""

import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    app_name: str = "Notes API"
    lab_mode: bool = False

    # VULNERABILITY 1: Hardcoded secret key
    # This is a security vulnerability - secrets should never be hardcoded
    # SAST tools like Semgrep, Bandit, or Trivy will detect this

    # FIX: Use environment variables for secrets
    # Uncomment the lines below and remove hardcoded values:
    secret_key: str = Field(..., min_length=32)
    api_token: str = Field(..., min_length=20)
    #
    # Then load from environment:
    class Config:
        env_file = ".env"
        case_sensitive = False
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.secret_key.startswith("hardcoded"):
            raise ValueError("Secret key must be set via environment variable")

    class Config:
        env_prefix = "APP_"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings(
        lab_mode=os.getenv("LAB_MODE", "0") == "1"
    )
