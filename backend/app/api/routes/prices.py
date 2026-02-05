"""
Price data API routes including WebSocket for real-time updates.
"""
import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.price import PriceHistory
from app.schemas.price import PriceData, PriceHistoryResponse, MarketOverview, AIAnalysisRequest, AIAnalysisResponse
from app.services.bybit import bybit_client
from app.services.ai_analysis import ai_service
from app.config import settings

router = APIRouter(prefix="/prices", tags=["Prices"])


# =============================================================================
# WebSocket Connection Manager
# =============================================================================

class PriceWebSocketManager:
    """Manages WebSocket connections for real-time price streaming."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"✓ Price WebSocket client connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"✗ Price WebSocket client disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, data: dict):
        """Broadcast price update to all connected clients."""
        if not self.active_connections:
            return
        
        message = json.dumps(data, default=str)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)


# Global WebSocket manager
ws_manager = PriceWebSocketManager()


# =============================================================================
# REST Endpoints
# =============================================================================

@router.get("/current", response_model=MarketOverview)
async def get_current_prices():
    """
    Get current prices for all tracked symbols.
    """
    prices = bybit_client.get_current_prices()
    
    price_list = []
    for symbol in settings.supported_symbols:
        if symbol in prices:
            p = prices[symbol]
            price_list.append(PriceData(
                symbol=p['symbol'],
                price=p['price'],
                high_24h=p.get('high_24h'),
                low_24h=p.get('low_24h'),
                volume_24h=p.get('volume_24h'),
                change_24h_percent=p.get('change_24h_percent'),
                timestamp=p.get('timestamp', datetime.utcnow())
            ))
    
    return MarketOverview(
        prices=price_list,
        last_updated=datetime.utcnow()
    )


@router.get("/current/{symbol}", response_model=PriceData)
async def get_current_price(symbol: str):
    """
    Get current price for a specific symbol.
    """
    symbol = symbol.upper()
    
    if symbol not in settings.supported_symbols:
        raise HTTPException(
            status_code=404,
            detail=f"Symbol not supported. Available: {', '.join(settings.supported_symbols)}"
        )
    
    price_data = bybit_client.get_price(symbol)
    
    if not price_data:
        raise HTTPException(
            status_code=503,
            detail="Price data not available. Please try again."
        )
    
    return PriceData(
        symbol=price_data['symbol'],
        price=price_data['price'],
        high_24h=price_data.get('high_24h'),
        low_24h=price_data.get('low_24h'),
        volume_24h=price_data.get('volume_24h'),
        change_24h_percent=price_data.get('change_24h_percent'),
        timestamp=price_data.get('timestamp', datetime.utcnow())
    )


@router.get("/history/{symbol}", response_model=PriceHistoryResponse)
async def get_price_history(
    symbol: str,
    period: str = Query("24h", regex="^(1h|24h|7d|30d)$"),
    db: Session = Depends(get_db)
):
    """
    Get historical price data for charting.
    
    Periods: 1h, 24h, 7d, 30d
    """
    symbol = symbol.upper()
    
    if symbol not in settings.supported_symbols:
        raise HTTPException(
            status_code=404,
            detail=f"Symbol not supported. Available: {', '.join(settings.supported_symbols)}"
        )
    
    # Calculate time range
    now = datetime.utcnow()
    period_map = {
        "1h": timedelta(hours=1),
        "24h": timedelta(hours=24),
        "7d": timedelta(days=7),
        "30d": timedelta(days=30)
    }
    start_time = now - period_map[period]
    
    # Query history
    history = db.query(PriceHistory).filter(
        PriceHistory.symbol == symbol,
        PriceHistory.timestamp >= start_time
    ).order_by(PriceHistory.timestamp.asc()).all()
    
    # If no history, generate mock data points from current price
    if not history:
        current = bybit_client.get_price(symbol)
        if current:
            # Generate simple mock history for demo
            data_points = []
            base_price = current['price']
            num_points = {"1h": 60, "24h": 96, "7d": 168, "30d": 180}[period]
            interval = period_map[period] / num_points
            
            import random
            for i in range(num_points):
                # Add some random variation
                variation = random.uniform(-0.02, 0.02) * base_price
                mock_price = base_price + variation
                mock_time = start_time + (interval * i)
                data_points.append({
                    "price": round(mock_price, 2),
                    "timestamp": mock_time
                })
            
            return PriceHistoryResponse(
                symbol=symbol,
                data=data_points,
                period=period
            )
    
    return PriceHistoryResponse(
        symbol=symbol,
        data=[{"price": h.price, "timestamp": h.timestamp} for h in history],
        period=period
    )


@router.get("/symbols")
async def get_supported_symbols():
    """
    Get list of supported trading symbols.
    """
    return {
        "symbols": settings.supported_symbols,
        "count": len(settings.supported_symbols)
    }


# =============================================================================
# AI Analysis Endpoint
# =============================================================================

@router.post("/analyze", response_model=AIAnalysisResponse)
async def analyze_market(request: AIAnalysisRequest):
    """
    Get AI-powered market analysis.
    """
    # Validate symbols
    invalid_symbols = [s for s in request.symbols if s not in settings.supported_symbols]
    if invalid_symbols:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid symbols: {', '.join(invalid_symbols)}"
        )
    
    # Get current prices
    prices = bybit_client.get_current_prices()
    
    # Generate analysis
    result = await ai_service.analyze_market(prices, request.symbols)
    
    return AIAnalysisResponse(
        analysis=result['analysis'],
        symbols_analyzed=result['symbols_analyzed'],
        sentiment=result['sentiment'],
        timestamp=result['timestamp']
    )


# =============================================================================
# WebSocket Endpoint
# =============================================================================

@router.websocket("/ws")
async def price_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time price streaming.
    
    Sends price updates as they come in from Bybit.
    """
    await ws_manager.connect(websocket)
    
    try:
        # Send current prices immediately on connect
        current_prices = bybit_client.get_current_prices()
        if current_prices:
            # Convert any datetime objects to ISO format strings
            serializable_prices = {}
            for symbol, data in current_prices.items():
                serializable_data = {
                    k: v.isoformat() if isinstance(v, datetime) else v
                    for k, v in data.items()
                }
                serializable_prices[symbol] = serializable_data
            
            await websocket.send_json({
                "type": "snapshot",
                "data": serializable_prices,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Keep connection alive and listen for client messages
        while True:
            try:
                # Wait for any client message (ping/pong or close)
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=30.0
                )
                
                # Handle ping
                if data == "ping":
                    await websocket.send_text("pong")
                    
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                try:
                    await websocket.send_text("ping")
                except Exception:
                    break
                    
    except WebSocketDisconnect:
        pass
    finally:
        ws_manager.disconnect(websocket)


# =============================================================================
# Callback for Bybit price updates
# =============================================================================

async def on_price_update(price_data: dict):
    """
    Callback function called when Bybit sends a price update.
    Broadcasts to all connected WebSocket clients.
    """
    # Serialize any datetime objects
    serializable_data = {
        k: v.isoformat() if isinstance(v, datetime) else v
        for k, v in price_data.items()
    }
    
    await ws_manager.broadcast({
        "type": "update",
        "data": serializable_data,
        "timestamp": datetime.utcnow().isoformat()
    })


# Register callback with Bybit client
bybit_client.add_callback(on_price_update)
