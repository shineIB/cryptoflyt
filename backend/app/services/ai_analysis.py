"""
AI-powered market analysis using Google Gemini.
"""
import asyncio
from datetime import datetime
from typing import List, Optional

from app.config import settings

# Optional Gemini import
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class AIAnalysisService:
    """
    AI-powered market analysis using Google Gemini.
    
    Provides:
    - Market sentiment analysis
    - Price movement explanations
    - Trading insights (educational, not financial advice)
    """
    
    def __init__(self):
        self.api_key = settings.google_api_key
        self.model = None
        
        if GEMINI_AVAILABLE and self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
    
    @property
    def is_available(self) -> bool:
        """Check if AI analysis is available."""
        return self.model is not None
    
    async def analyze_market(
        self,
        prices: dict,
        symbols: List[str]
    ) -> dict:
        """
        Generate AI analysis of current market conditions.
        
        Args:
            prices: Dict of current prices {symbol: price_data}
            symbols: List of symbols to analyze
            
        Returns:
            Analysis dict with text and sentiment
        """
        if not self.is_available:
            return self._mock_analysis(prices, symbols)
        
        try:
            # Build context from price data
            price_context = self._build_price_context(prices, symbols)
            
            prompt = f"""You are a cryptocurrency market analyst. Analyze the following market data and provide insights.

IMPORTANT: This is for educational purposes only. Do not provide financial advice.

Current Market Data:
{price_context}

Please provide:
1. **Market Overview**: Brief summary of current market conditions (2-3 sentences)
2. **Key Observations**: Notable price movements or patterns (bullet points)
3. **Market Sentiment**: Overall sentiment (Bullish/Bearish/Neutral) with brief reasoning
4. **Things to Watch**: What traders might want to monitor (2-3 points)

Keep the response concise and factual. Focus on the data provided.
"""
            
            # Call Gemini API
            response = await asyncio.to_thread(
                self.model.generate_content, prompt
            )
            
            # Determine sentiment from response
            sentiment = self._extract_sentiment(response.text)
            
            return {
                "analysis": response.text,
                "symbols_analyzed": symbols,
                "sentiment": sentiment,
                "timestamp": datetime.utcnow(),
                "source": "gemini"
            }
            
        except Exception as e:
            print(f"AI analysis error: {e}")
            return self._mock_analysis(prices, symbols)
    
    async def explain_price_movement(
        self,
        symbol: str,
        change_percent: float,
        current_price: float
    ) -> str:
        """
        Generate explanation for a significant price movement.
        
        Args:
            symbol: Trading pair
            change_percent: 24h change percentage
            current_price: Current price
            
        Returns:
            Explanation text
        """
        if not self.is_available:
            return self._mock_explanation(symbol, change_percent)
        
        try:
            direction = "increased" if change_percent > 0 else "decreased"
            
            prompt = f"""The cryptocurrency {symbol} has {direction} by {abs(change_percent):.2f}% in the last 24 hours.
Current price: ${current_price:,.2f}

Provide a brief (2-3 sentences) general explanation of what might cause such price movements in crypto markets.
Do not speculate on specific news or events. Keep it educational and general.
Do not provide financial advice."""
            
            response = await asyncio.to_thread(
                self.model.generate_content, prompt
            )
            
            return response.text
            
        except Exception as e:
            print(f"AI explanation error: {e}")
            return self._mock_explanation(symbol, change_percent)
    
    def _build_price_context(self, prices: dict, symbols: List[str]) -> str:
        """Build context string from price data."""
        lines = []
        for symbol in symbols:
            if symbol in prices:
                p = prices[symbol]
                change = p.get('change_24h_percent', 0)
                direction = "🟢" if change >= 0 else "🔴"
                lines.append(
                    f"- {symbol}: ${p['price']:,.2f} ({direction} {change:+.2f}% 24h)"
                )
        return "\n".join(lines) if lines else "No price data available"
    
    def _extract_sentiment(self, text: str) -> str:
        """Extract sentiment from analysis text."""
        text_lower = text.lower()
        if "bullish" in text_lower:
            return "bullish"
        elif "bearish" in text_lower:
            return "bearish"
        return "neutral"
    
    def _mock_analysis(self, prices: dict, symbols: List[str]) -> dict:
        """Generate mock analysis when AI is not available."""
        # Calculate basic stats
        total_change = 0
        count = 0
        
        for symbol in symbols:
            if symbol in prices:
                total_change += prices[symbol].get('change_24h_percent', 0)
                count += 1
        
        avg_change = total_change / count if count > 0 else 0
        sentiment = "bullish" if avg_change > 2 else "bearish" if avg_change < -2 else "neutral"
        
        analysis = f"""## Market Overview

The cryptocurrency market is showing {"positive" if avg_change > 0 else "negative"} momentum with an average change of {avg_change:+.2f}% across tracked assets.

### Key Observations

"""
        for symbol in symbols:
            if symbol in prices:
                p = prices[symbol]
                change = p.get('change_24h_percent', 0)
                emoji = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                analysis += f"- {emoji} **{symbol}**: ${p['price']:,.2f} ({change:+.2f}%)\n"
        
        analysis += f"""
### Market Sentiment: {sentiment.upper()}

Based on price action, the market appears {sentiment}. {"Buyers are showing strength." if sentiment == "bullish" else "Sellers are in control." if sentiment == "bearish" else "The market is consolidating."}

### Things to Watch

1. Monitor support and resistance levels
2. Watch for volume changes that confirm trend direction
3. Keep an eye on Bitcoin dominance for altcoin movements

---
*Note: Connect Google Gemini API for AI-powered insights. This is a basic analysis.*
"""
        
        return {
            "analysis": analysis,
            "symbols_analyzed": symbols,
            "sentiment": sentiment,
            "timestamp": datetime.utcnow(),
            "source": "mock"
        }
    
    def _mock_explanation(self, symbol: str, change_percent: float) -> str:
        """Generate mock explanation."""
        direction = "increase" if change_percent > 0 else "decrease"
        
        return f"""
Price {"increases" if change_percent > 0 else "decreases"} in cryptocurrency markets can be driven by various factors including market sentiment, trading volume, broader economic conditions, and supply/demand dynamics. A {abs(change_percent):.1f}% {direction} is {"significant" if abs(change_percent) > 5 else "moderate"} {"and may indicate strong" if abs(change_percent) > 5 else "and reflects normal"} market {"momentum" if change_percent > 0 else "pressure"}.

*Connect Google Gemini API for more detailed AI analysis.*
        """.strip()


# Global instance
ai_service = AIAnalysisService()
