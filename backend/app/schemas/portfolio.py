"""
Pydantic schemas for Portfolio API.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class HoldingBase(BaseModel):
    """Base holding schema."""
    symbol: str
    amount: float
    average_buy_price: Optional[float] = None


class HoldingCreate(HoldingBase):
    """Schema for creating a holding."""
    pass


class HoldingUpdate(BaseModel):
    """Schema for updating a holding."""
    amount: Optional[float] = None
    average_buy_price: Optional[float] = None


class HoldingResponse(HoldingBase):
    """Schema for holding response."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    # Calculated fields (added by API)
    current_price: Optional[float] = None
    current_value: Optional[float] = None
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None
    
    class Config:
        from_attributes = True


class PortfolioSummary(BaseModel):
    """Schema for portfolio summary."""
    total_value: float
    total_pnl: float
    total_pnl_percent: float
    holdings: List[HoldingResponse]
