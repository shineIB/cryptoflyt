"""
CryptoFlyt - Real-time Crypto Dashboard with Alerts
Main FastAPI application entry point.
"""
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.database import init_db
from app.services.bybit import bybit_client
from app.api.routes import auth, alerts, portfolio, prices


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print("🚀 Starting CryptoFlyt...")
    
    # Initialize database tables
    init_db()
    print("✓ Database initialized")
    
    # Start Bybit WebSocket connection
    asyncio.create_task(bybit_client.listen())
    print("✓ Bybit WebSocket connecting...")
    
    yield
    
    # Shutdown
    print("👋 Shutting down CryptoFlyt...")
    await bybit_client.disconnect()


# Create FastAPI app
app = FastAPI(
    title="CryptoFlyt API",
    description="Real-time cryptocurrency dashboard with alerts and portfolio tracking",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(portfolio.router, prefix="/api")
app.include_router(prices.router, prefix="/api")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "CryptoFlyt API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    prices = bybit_client.get_current_prices()
    
    return {
        "status": "healthy",
        "bybit_connected": len(prices) > 0,
        "symbols_tracking": list(prices.keys()),
        "ai_available": bool(settings.google_api_key),
        "telegram_configured": bool(settings.telegram_bot_token)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
