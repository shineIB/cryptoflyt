"""
Price alert database model.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class AlertCondition(str, enum.Enum):
    """Alert trigger conditions."""
    ABOVE = "above"  # Trigger when price goes above target
    BELOW = "below"  # Trigger when price goes below target


class Alert(Base):
    """Price alert model."""
    
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Alert configuration
    symbol = Column(String(20), nullable=False, index=True)  # e.g., "BTCUSDT"
    target_price = Column(Float, nullable=False)
    condition = Column(Enum(AlertCondition), nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_triggered = Column(Boolean, default=False)
    triggered_at = Column(DateTime, nullable=True)
    triggered_price = Column(Float, nullable=True)
    
    # Notification settings
    notify_telegram = Column(Boolean, default=True)
    notify_email = Column(Boolean, default=False)
    
    # Metadata
    note = Column(String(500), nullable=True)  # User's note about this alert
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="alerts")
    
    def __repr__(self):
        return f"<Alert {self.symbol} {self.condition.value} {self.target_price}>"
    
    def check_condition(self, current_price: float) -> bool:
        """Check if alert condition is met."""
        if self.condition == AlertCondition.ABOVE:
            return current_price >= self.target_price
        else:  # BELOW
            return current_price <= self.target_price
