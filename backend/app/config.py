"""Application configuration settings."""

import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Settings
    api_title: str = "Enviro Governance Platform API"
    api_version: str = "0.1.0"
    api_v1_str: str = "/api/v1"
    
    # Database
    database_url: str = "postgresql://user:password@localhost/enviro_governance"
    database_echo: bool = False
    database_pool_size: int = 20
    database_max_overflow: int = 10
    
    # Logging
    log_level: str = "INFO"
    
    # CORS
    cors_origins: list = ["http://localhost:3000", "http://localhost:8000"]
    cors_credentials: bool = True
    cors_methods: list = ["*"]
    cors_headers: list = ["*"]
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Environment
    environment: str = "development"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
