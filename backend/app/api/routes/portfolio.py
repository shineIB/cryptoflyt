"""
Portfolio management API routes.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.portfolio import PortfolioHolding
from app.schemas.portfolio import HoldingCreate, HoldingUpdate, HoldingResponse, PortfolioSummary
from app.services.bybit import bybit_client
from app.config import settings

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])


@router.get("", response_model=PortfolioSummary)
async def get_portfolio(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's complete portfolio with current values.
    """
    holdings = db.query(PortfolioHolding).filter(
        PortfolioHolding.user_id == current_user.id
    ).all()
    
    # Get current prices
    current_prices = bybit_client.get_current_prices()
    
    # Calculate values for each holding
    holdings_response = []
    total_value = 0
    total_cost = 0
    
    for holding in holdings:
        price_data = current_prices.get(holding.symbol, {})
        current_price = price_data.get('price', 0)
        current_value = holding.amount * current_price
        
        # Calculate P&L
        pnl = 0
        pnl_percent = 0
        if holding.average_buy_price and holding.average_buy_price > 0:
            cost_basis = holding.amount * holding.average_buy_price
            pnl = current_value - cost_basis
            pnl_percent = (pnl / cost_basis) * 100 if cost_basis > 0 else 0
            total_cost += cost_basis
        
        total_value += current_value
        
        holdings_response.append(HoldingResponse(
            id=holding.id,
            user_id=holding.user_id,
            symbol=holding.symbol,
            amount=holding.amount,
            average_buy_price=holding.average_buy_price,
            created_at=holding.created_at,
            updated_at=holding.updated_at,
            current_price=round(current_price, 2),
            current_value=round(current_value, 2),
            pnl=round(pnl, 2),
            pnl_percent=round(pnl_percent, 2)
        ))
    
    # Calculate total P&L
    total_pnl = total_value - total_cost if total_cost > 0 else 0
    total_pnl_percent = (total_pnl / total_cost) * 100 if total_cost > 0 else 0
    
    return PortfolioSummary(
        total_value=round(total_value, 2),
        total_pnl=round(total_pnl, 2),
        total_pnl_percent=round(total_pnl_percent, 2),
        holdings=holdings_response
    )


@router.post("/holdings", response_model=HoldingResponse, status_code=status.HTTP_201_CREATED)
async def add_holding(
    holding_data: HoldingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a new holding to portfolio.
    """
    # Validate symbol
    if holding_data.symbol not in settings.supported_symbols:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported symbol. Supported: {', '.join(settings.supported_symbols)}"
        )
    
    # Check if holding already exists for this symbol
    existing = db.query(PortfolioHolding).filter(
        PortfolioHolding.user_id == current_user.id,
        PortfolioHolding.symbol == holding_data.symbol
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Holding for {holding_data.symbol} already exists. Use PATCH to update."
        )
    
    # Create holding
    holding = PortfolioHolding(
        user_id=current_user.id,
        symbol=holding_data.symbol,
        amount=holding_data.amount,
        average_buy_price=holding_data.average_buy_price
    )
    
    db.add(holding)
    db.commit()
    db.refresh(holding)
    
    # Add current price info
    price_data = bybit_client.get_price(holding.symbol)
    current_price = price_data.get('price', 0) if price_data else 0
    
    return HoldingResponse(
        id=holding.id,
        user_id=holding.user_id,
        symbol=holding.symbol,
        amount=holding.amount,
        average_buy_price=holding.average_buy_price,
        created_at=holding.created_at,
        updated_at=holding.updated_at,
        current_price=round(current_price, 2),
        current_value=round(holding.amount * current_price, 2),
        pnl=0,
        pnl_percent=0
    )


@router.patch("/holdings/{holding_id}", response_model=HoldingResponse)
async def update_holding(
    holding_id: int,
    holding_data: HoldingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a holding in portfolio.
    """
    holding = db.query(PortfolioHolding).filter(
        PortfolioHolding.id == holding_id,
        PortfolioHolding.user_id == current_user.id
    ).first()
    
    if not holding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Holding not found"
        )
    
    # Update fields
    if holding_data.amount is not None:
        holding.amount = holding_data.amount
    if holding_data.average_buy_price is not None:
        holding.average_buy_price = holding_data.average_buy_price
    
    db.commit()
    db.refresh(holding)
    
    # Calculate current values
    price_data = bybit_client.get_price(holding.symbol)
    current_price = price_data.get('price', 0) if price_data else 0
    current_value = holding.amount * current_price
    
    pnl = 0
    pnl_percent = 0
    if holding.average_buy_price and holding.average_buy_price > 0:
        cost_basis = holding.amount * holding.average_buy_price
        pnl = current_value - cost_basis
        pnl_percent = (pnl / cost_basis) * 100 if cost_basis > 0 else 0
    
    return HoldingResponse(
        id=holding.id,
        user_id=holding.user_id,
        symbol=holding.symbol,
        amount=holding.amount,
        average_buy_price=holding.average_buy_price,
        created_at=holding.created_at,
        updated_at=holding.updated_at,
        current_price=round(current_price, 2),
        current_value=round(current_value, 2),
        pnl=round(pnl, 2),
        pnl_percent=round(pnl_percent, 2)
    )


@router.delete("/holdings/{holding_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_holding(
    holding_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove a holding from portfolio.
    """
    holding = db.query(PortfolioHolding).filter(
        PortfolioHolding.id == holding_id,
        PortfolioHolding.user_id == current_user.id
    ).first()
    
    if not holding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Holding not found"
        )
    
    db.delete(holding)
    db.commit()
