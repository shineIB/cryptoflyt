"""
Portfolio holdings database model.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class PortfolioHolding(Base):
    """User's crypto holdings."""
    
    __tablename__ = "portfolio_holdings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Holding details
    symbol = Column(String(20), nullable=False)  # e.g., "BTCUSDT"
    amount = Column(Float, nullable=False)  # e.g., 0.5 BTC
    average_buy_price = Column(Float, nullable=True)  # Optional: track cost basis
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="holdings")
    
    def __repr__(self):
        return f"<Holding {self.amount} {self.symbol}>"
    
    def calculate_value(self, current_price: float) -> float:
        """Calculate current value of holding."""
        return self.amount * current_price
    
    def calculate_pnl(self, current_price: float) -> dict:
        """Calculate profit/loss if average buy price is set."""
        if not self.average_buy_price:
            return {"pnl": 0, "pnl_percent": 0}
        
        current_value = self.calculate_value(current_price)
        cost_basis = self.amount * self.average_buy_price
        pnl = current_value - cost_basis
        pnl_percent = (pnl / cost_basis) * 100 if cost_basis > 0 else 0
        
        return {
            "pnl": round(pnl, 2),
            "pnl_percent": round(pnl_percent, 2)
        }
