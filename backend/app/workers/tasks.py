"""
Celery background tasks for CryptoFlyt.
"""
import asyncio
from datetime import datetime
from app.workers.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.price import PriceHistory
from app.services.bybit import bybit_client
from app.services.alert_checker import AlertChecker
from app.config import settings


@celery_app.task(name='app.workers.tasks.check_price_alerts')
def check_price_alerts():
    """
    Periodic task to check if any price alerts should be triggered.
    Runs every 60 seconds.
    """
    db = SessionLocal()
    try:
        # Get current prices
        prices = bybit_client.get_current_prices()
        
        # Create AlertChecker instance
        checker = AlertChecker(db)
        
        # Check alerts for each symbol (using asyncio to handle async methods)
        async def check_all_alerts():
            all_triggered = []
            for symbol, price_data in prices.items():
                triggered = await checker.check_alerts(symbol, price_data['price'])
                all_triggered.extend(triggered)
            return all_triggered
        
        # Run the async function
        all_triggered = asyncio.run(check_all_alerts())
        
        return {
            'status': 'success',
            'alerts_checked': len(prices),
            'alerts_triggered': len(all_triggered),
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }
    finally:
        db.close()


@celery_app.task(name='app.workers.tasks.update_price_history')
def update_price_history():
    """
    Periodic task to save current prices to historical database.
    Runs every 5 minutes.
    """
    db = SessionLocal()
    try:
        prices = bybit_client.get_current_prices()
        records_created = 0
        
        for symbol, data in prices.items():
            # Create price history record
            price_record = PriceHistory(
                symbol=symbol,
                price=data['price'],
                high_24h=data.get('high_24h'),
                low_24h=data.get('low_24h'),
                volume_24h=data.get('volume_24h'),
                timestamp=datetime.utcnow()
            )
            db.add(price_record)
            records_created += 1
        
        db.commit()
        
        return {
            'status': 'success',
            'records_created': records_created,
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        db.rollback()
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }
    finally:
        db.close()


@celery_app.task(name='app.workers.tasks.send_notification')
def send_notification(user_id: int, message: str, notification_type: str = 'alert'):
    """
    Task to send notifications to users.
    Can be called asynchronously when alerts trigger.
    """
    db = SessionLocal()
    try:
        from app.services.notifier import notifier
        from app.models.user import User
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {'status': 'error', 'error': 'User not found'}
        
        # Send notification based on user preferences
        if user.telegram_chat_id:
            notifier.send_telegram(user.telegram_chat_id, message)
        
        # Could add email, SMS, push notifications here
        
        return {
            'status': 'success',
            'user_id': user_id,
            'notification_type': notification_type,
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }
    finally:
        db.close()
