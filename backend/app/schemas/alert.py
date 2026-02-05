"""
Pydantic schemas for Alert API.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.models.alert import AlertCondition


class AlertBase(BaseModel):
    """Base alert schema."""
    symbol: str
    target_price: float
    condition: AlertCondition
    note: Optional[str] = None
    notify_telegram: bool = True
    notify_email: bool = False


class AlertCreate(AlertBase):
    """Schema for creating an alert."""
    pass


class AlertUpdate(BaseModel):
    """Schema for updating an alert."""
    target_price: Optional[float] = None
    condition: Optional[AlertCondition] = None
    is_active: Optional[bool] = None
    note: Optional[str] = None
    notify_telegram: Optional[bool] = None
    notify_email: Optional[bool] = None


class AlertResponse(AlertBase):
    """Schema for alert response."""
    id: int
    user_id: int
    is_active: bool
    is_triggered: bool
    triggered_at: Optional[datetime]
    triggered_price: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AlertHistoryResponse(BaseModel):
    """Schema for alert history response."""
    id: int
    alert_id: int
    symbol: str
    target_price: float
    triggered_price: float
    condition: str
    telegram_sent: bool
    email_sent: bool
    triggered_at: datetime
    
    class Config:
        from_attributes = True
