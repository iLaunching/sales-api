"""
Configuration management for Sales API
Loads settings from environment variables
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    DEBUG: bool = False
    PORT: int = int(os.getenv("PORT", "8080"))
    ENVIRONMENT: str = "production"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/sales_db"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_SESSION_TTL: int = 86400  # 24 hours
    
    # Qdrant Vector Database (Optional - for Phase 1)
    QDRANT_URL: str = ""
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION_NAME: str = "sales_knowledge"
    QDRANT_ENABLED: bool = False  # Set to True when Qdrant is configured
    
    # LLM Configuration
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    DEFAULT_LLM_MODEL: str = "gpt-4o-mini"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 1000
    
    # MCP Server (Optional - for Phase 1)
    MCP_SERVER_URL: str = ""
    MCP_SERVER_TIMEOUT: int = 30
    MCP_ENABLED: bool = False  # Set to True when MCP server is configured
    
    # Auth API Integration (Optional - for Phase 3)
    AUTH_API_URL: str = ""
    AUTH_API_KEY: str = ""
    
    # Lead Qualification
    HIGH_QUALITY_SCORE_THRESHOLD: int = 70
    MEDIUM_QUALITY_SCORE_THRESHOLD: int = 40
    
    # A/B Testing
    AB_TESTING_ENABLED: bool = True
    AB_TEST_VARIANTS: List[str] = ["control", "variant_a", "variant_b"]
    
    # Analytics
    CONVERSION_TRACKING_ENABLED: bool = True
    ANALYTICS_BATCH_SIZE: int = 100
    
    # Monitoring
    SENTRY_DSN: str = ""
    LOG_LEVEL: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# Global settings instance
settings = Settings()
