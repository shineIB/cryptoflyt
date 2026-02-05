"""
Notification service for sending alerts via Telegram, Email, etc.
"""
import asyncio
from typing import Optional
import httpx

from app.config import settings


class NotificationService:
    """
    Service for sending notifications through various channels.
    
    Supports:
    - Telegram (via Bot API)
    - Email (placeholder for future implementation)
    - Push notifications (placeholder for future implementation)
    """
    
    def __init__(self):
        self.telegram_token = settings.telegram_bot_token
        self.telegram_api_url = f"https://api.telegram.org/bot{self.telegram_token}"
    
    async def send_telegram(self, chat_id: str, message: str) -> bool:
        """
        Send a message via Telegram bot.
        
        Args:
            chat_id: Telegram chat ID of the recipient
            message: Message text (supports Markdown)
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.telegram_token:
            print("⚠ Telegram bot token not configured")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.telegram_api_url}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": message,
                        "parse_mode": "Markdown"
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    print(f"✓ Telegram message sent to {chat_id}")
                    return True
                else:
                    print(f"✗ Telegram API error: {response.text}")
                    return False
                    
        except Exception as e:
            print(f"✗ Failed to send Telegram message: {e}")
            return False
    
    async def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """
        Send an email notification.
        
        Placeholder for email implementation (SendGrid, AWS SES, etc.)
        """
        # TODO: Implement email sending
        print(f"📧 Email notification (not implemented): {to_email} - {subject}")
        return False
    
    async def send_alert_notification(
        self,
        user,
        symbol: str,
        condition: str,
        target_price: float,
        triggered_price: float,
        note: Optional[str] = None
    ):
        """
        Send alert notification to user via all configured channels.
        
        Args:
            user: User model instance
            symbol: Trading pair
            condition: Alert condition ("above" or "below")
            target_price: User's target price
            triggered_price: Price that triggered the alert
            note: Optional user note
        """
        emoji = "📈" if condition == "above" else "📉"
        
        message = f"""
{emoji} *CryptoFlyt Alert!*

*{symbol}* hit your target!

Condition: Price {condition} ${target_price:,.2f}
Triggered at: ${triggered_price:,.2f}

{f"📝 {note}" if note else ""}

---
_Manage alerts at cryptoflyt.com_
        """.strip()
        
        tasks = []
        
        # Telegram
        if user.telegram_notifications and user.telegram_chat_id:
            tasks.append(self.send_telegram(user.telegram_chat_id, message))
        
        # Email
        if user.email_notifications:
            subject = f"🔔 {symbol} Alert Triggered - CryptoFlyt"
            tasks.append(self.send_email(user.email, subject, message))
        
        if tasks:
            await asyncio.gather(*tasks)


# Helper function to get chat ID from Telegram
async def get_telegram_chat_id_instructions() -> str:
    """Return instructions for users to get their Telegram chat ID."""
    return """
To receive Telegram notifications:

1. Search for @CryptoFlytBot on Telegram (or your bot name)
2. Start a chat with the bot by clicking "Start"
3. Send the message: /start
4. The bot will reply with your Chat ID
5. Copy that ID and paste it in your profile settings

Note: Make sure you've started a conversation with the bot, 
otherwise it cannot send you messages.
    """.strip()
