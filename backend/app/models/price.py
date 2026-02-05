"""
Price history database model.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Index

from app.core.database import Base


class PriceHistory(Base):
    """Historical price data for charting."""
    
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Price data
    symbol = Column(String(20), nullable=False)
    price = Column(Float, nullable=False)
    high_24h = Column(Float, nullable=True)
    low_24h = Column(Float, nullable=True)
    volume_24h = Column(Float, nullable=True)
    change_24h_percent = Column(Float, nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Composite index for efficient queries
    __table_args__ = (
        Index('idx_symbol_timestamp', 'symbol', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<Price {self.symbol} ${self.price} at {self.timestamp}>"


class AlertHistory(Base):
    """Log of triggered alerts."""
    
    __tablename__ = "alert_history"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Alert reference
    alert_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    
    # Snapshot of alert when triggered
    symbol = Column(String(20), nullable=False)
    target_price = Column(Float, nullable=False)
    triggered_price = Column(Float, nullable=False)
    condition = Column(String(20), nullable=False)
    
    # Notification status
    telegram_sent = Column(Integer, default=False)
    email_sent = Column(Integer, default=False)
    
    # Timestamp
    triggered_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<AlertHistory {self.symbol} triggered at ${self.triggered_price}>"
