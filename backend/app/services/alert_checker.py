"""
Alert checking service - monitors prices and triggers alerts.
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.alert import Alert, AlertCondition
from app.models.price import AlertHistory
from app.services.notifier import NotificationService


class AlertChecker:
    """
    Service to check and trigger price alerts.
    
    Called whenever a new price update is received from Bybit.
    Checks all active alerts for the symbol and triggers notifications.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.notifier = NotificationService()
    
    async def check_alerts(self, symbol: str, current_price: float) -> List[Alert]:
        """
        Check all active alerts for a symbol and trigger if conditions are met.
        
        Args:
            symbol: Trading pair (e.g., "BTCUSDT")
            current_price: Current market price
            
        Returns:
            List of triggered alerts
        """
        # Get all active, non-triggered alerts for this symbol
        alerts = self.db.query(Alert).filter(
            Alert.symbol == symbol,
            Alert.is_active == True,
            Alert.is_triggered == False
        ).all()
        
        triggered_alerts = []
        
        for alert in alerts:
            if alert.check_condition(current_price):
                await self._trigger_alert(alert, current_price)
                triggered_alerts.append(alert)
        
        if triggered_alerts:
            self.db.commit()
        
        return triggered_alerts
    
    async def _trigger_alert(self, alert: Alert, triggered_price: float):
        """
        Trigger an alert and send notifications.
        
        Args:
            alert: The alert to trigger
            triggered_price: The price that triggered the alert
        """
        # Update alert status
        alert.is_triggered = True
        alert.triggered_at = datetime.utcnow()
        alert.triggered_price = triggered_price
        
        # Create history record
        history = AlertHistory(
            alert_id=alert.id,
            user_id=alert.user_id,
            symbol=alert.symbol,
            target_price=alert.target_price,
            triggered_price=triggered_price,
            condition=alert.condition.value,
            triggered_at=datetime.utcnow()
        )
        self.db.add(history)
        
        # Send notifications
        user = alert.user
        notification_message = self._format_notification(alert, triggered_price)
        
        # Telegram notification
        if alert.notify_telegram and user.telegram_chat_id and user.telegram_notifications:
            success = await self.notifier.send_telegram(
                chat_id=user.telegram_chat_id,
                message=notification_message
            )
            history.telegram_sent = success
        
        # Log notification (email would go here)
        print(f"🔔 Alert triggered: {alert.symbol} {alert.condition.value} ${alert.target_price} (actual: ${triggered_price})")
    
    def _format_notification(self, alert: Alert, triggered_price: float) -> str:
        """Format the notification message."""
        direction = "above" if alert.condition == AlertCondition.ABOVE else "below"
        emoji = "📈" if alert.condition == AlertCondition.ABOVE else "📉"
        
        message = f"""
{emoji} *CryptoFlyt Alert Triggered!*

*{alert.symbol}* is now {direction} your target!

Target Price: ${alert.target_price:,.2f}
Current Price: ${triggered_price:,.2f}

{f"Note: {alert.note}" if alert.note else ""}
        """.strip()
        
        return message
    
    def get_active_alerts_for_user(self, user_id: int) -> List[Alert]:
        """Get all active alerts for a user."""
        return self.db.query(Alert).filter(
            Alert.user_id == user_id,
            Alert.is_active == True
        ).all()
    
    def get_triggered_history(self, user_id: int, limit: int = 50) -> List[AlertHistory]:
        """Get alert trigger history for a user."""
        return self.db.query(AlertHistory).filter(
            AlertHistory.user_id == user_id
        ).order_by(AlertHistory.triggered_at.desc()).limit(limit).all()
