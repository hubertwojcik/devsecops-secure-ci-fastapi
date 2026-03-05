"""Application configuration with intentional security vulnerabilities."""

import os

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    app_name: str = "Notes API"
    lab_mode: bool = False

    # VULNERABILITY 1: Hardcoded secret key
    # This is a security vulnerability - secrets should never be hardcoded
    # SAST tools like Semgrep, Bandit, or Trivy will detect this

    # FIX: Use environment variables for secrets
    secret_key: str = Field(..., min_length=32)
    api_token: str = Field(..., min_length=20)

    class Config:
        env_file = ".env"
        case_sensitive = False
        env_prefix = "APP_"



def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings(
        lab_mode=os.getenv("LAB_MODE", "0") == "1"
    )
