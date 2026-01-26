"""
Configuration settings.
"""
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # App
    APP_NAME: str = "xBasis"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production-min-32-chars"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/xbasis"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # JWT
    JWT_SECRET: str = "jwt-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "https://xbasis.app",
    ]
    
    # AI Providers
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    DEFAULT_AI_MODEL: str = "claude-sonnet-4-20250514"
    
    # Deploy (Railway)
    RAILWAY_API_KEY: str = ""
    RAILWAY_PROJECT_ID: str = ""
    
    # GitHub
    GITHUB_WEBHOOK_SECRET: str = ""
    
    # Billing (Paddle)
    PADDLE_VENDOR_ID: str = ""
    PADDLE_API_KEY: str = ""
    PADDLE_WEBHOOK_SECRET: str = ""
    PADDLE_PRO_PRICE_ID: str = ""
    PADDLE_TEAM_PRICE_ID: str = ""
    
    # Plans
    PLAN_FREE_TOKENS: int = 10000
    PLAN_PRO_TOKENS: int = 100000
    PLAN_TEAM_TOKENS: int = 500000

    # Monitoring
    SENTRY_DSN: str = ""
    ENVIRONMENT: str = "development"

    # Email (Resend)
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "xBasis <noreply@xbasis.app>"
    APP_URL: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()