"""
Application configuration and settings.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App
    app_name: str = "CryptoFlyt"
    debug: bool = True
    
    # Database
    database_url: str = "postgresql://cryptoflyt:cryptoflyt_secret@localhost:5432/cryptoflyt"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Security
    secret_key: str = "your-super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    
    # External APIs
    google_api_key: str = ""
    telegram_bot_token: str = ""
    
    # Bybit WebSocket
    bybit_ws_url: str = "wss://stream.bybit.com/v5/public/spot"
    
    # Supported trading pairs
    supported_symbols: list = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT"]
    
    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
