"""
Pydantic schemas for Price API.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class PriceData(BaseModel):
    """Real-time price data from Bybit."""
    symbol: str
    price: float
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    volume_24h: Optional[float] = None
    change_24h_percent: Optional[float] = None
    timestamp: datetime


class PriceHistoryPoint(BaseModel):
    """Single price history data point."""
    price: float
    timestamp: datetime


class PriceHistoryResponse(BaseModel):
    """Price history for charting."""
    symbol: str
    data: List[PriceHistoryPoint]
    period: str  # "1h", "24h", "7d", "30d"


class MarketOverview(BaseModel):
    """Overview of all tracked markets."""
    prices: List[PriceData]
    last_updated: datetime


class AIAnalysisRequest(BaseModel):
    """Request for AI market analysis."""
    symbols: List[str]
    include_news: bool = True


class AIAnalysisResponse(BaseModel):
    """AI-generated market analysis."""
    analysis: str
    symbols_analyzed: List[str]
    sentiment: str  # "bullish", "bearish", "neutral"
    timestamp: datetime
