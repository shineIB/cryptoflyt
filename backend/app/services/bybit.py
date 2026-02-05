"""
Bybit WebSocket client for real-time price streaming.
"""
import json
import asyncio
from datetime import datetime
from typing import Dict, Callable, Optional
import aiohttp

from app.config import settings


class BybitWebSocketClient:
    """
    WebSocket client for Bybit real-time market data.
    
    Connects to Bybit's public spot WebSocket and streams
    real-time ticker data for configured symbols.
    """
    
    def __init__(self):
        self.ws_url = settings.bybit_ws_url
        self.symbols = settings.supported_symbols
        self.ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.running = False
        self.prices: Dict[str, dict] = {}
        self.callbacks: list[Callable] = []
        self._reconnect_delay = 5
    
    def add_callback(self, callback: Callable):
        """Add a callback function to be called on price updates."""
        self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable):
        """Remove a callback function."""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    async def _notify_callbacks(self, price_data: dict):
        """Notify all registered callbacks of price update."""
        for callback in self.callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(price_data)
                else:
                    callback(price_data)
            except Exception as e:
                print(f"Callback error: {e}")
    
    def get_current_prices(self) -> Dict[str, dict]:
        """Get the latest cached prices."""
        return self.prices.copy()
    
    def get_price(self, symbol: str) -> Optional[dict]:
        """Get the latest price for a specific symbol."""
        return self.prices.get(symbol)
    
    async def connect(self):
        """Establish WebSocket connection to Bybit."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        
        try:
            self.ws = await self.session.ws_connect(self.ws_url)
            print(f"✓ Connected to Bybit WebSocket")
            
            # Subscribe to ticker streams for all symbols
            subscribe_msg = {
                "op": "subscribe",
                "args": [f"tickers.{symbol}" for symbol in self.symbols]
            }
            await self.ws.send_json(subscribe_msg)
            print(f"✓ Subscribed to: {', '.join(self.symbols)}")
            
            return True
        except Exception as e:
            print(f"✗ Failed to connect to Bybit: {e}")
            return False
    
    async def disconnect(self):
        """Close WebSocket connection."""
        self.running = False
        if self.ws:
            await self.ws.close()
        if self.session:
            await self.session.close()
        print("✗ Disconnected from Bybit WebSocket")
    
    async def listen(self):
        """Listen for incoming WebSocket messages."""
        self.running = True
        
        while self.running:
            try:
                if self.ws is None or self.ws.closed:
                    success = await self.connect()
                    if not success:
                        await asyncio.sleep(self._reconnect_delay)
                        continue
                
                async for msg in self.ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        await self._handle_message(msg.data)
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        print(f"WebSocket error: {self.ws.exception()}")
                        break
                    elif msg.type == aiohttp.WSMsgType.CLOSED:
                        print("WebSocket closed by server")
                        break
                
            except Exception as e:
                print(f"WebSocket listen error: {e}")
            
            if self.running:
                print(f"Reconnecting in {self._reconnect_delay}s...")
                await asyncio.sleep(self._reconnect_delay)
    
    async def _handle_message(self, raw_data: str):
        """Process incoming WebSocket message."""
        try:
            data = json.loads(raw_data)
            
            # Handle ticker updates
            if data.get("topic", "").startswith("tickers."):
                ticker_data = data.get("data", {})
                symbol = ticker_data.get("symbol")
                
                if symbol:
                    price_data = {
                        "symbol": symbol,
                        "price": float(ticker_data.get("lastPrice", 0)),
                        "high_24h": float(ticker_data.get("highPrice24h", 0)),
                        "low_24h": float(ticker_data.get("lowPrice24h", 0)),
                        "volume_24h": float(ticker_data.get("volume24h", 0)),
                        "change_24h_percent": float(ticker_data.get("price24hPcnt", 0)) * 100,
                        "timestamp": datetime.utcnow()
                    }
                    
                    # Update cache
                    self.prices[symbol] = price_data
                    
                    # Notify callbacks
                    await self._notify_callbacks(price_data)
            
            # Handle subscription confirmation
            elif data.get("op") == "subscribe":
                if data.get("success"):
                    print(f"✓ Subscription confirmed")
                else:
                    print(f"✗ Subscription failed: {data.get('ret_msg')}")
                    
        except json.JSONDecodeError:
            print(f"Invalid JSON received: {raw_data[:100]}")
        except Exception as e:
            print(f"Message handling error: {e}")


# Global instance
bybit_client = BybitWebSocketClient()
