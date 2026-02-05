"""
User database model.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean

from app.core.database import Base


class User(Base):
    """User account model."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile
    telegram_chat_id = Column(String(100), nullable=True)  # For Telegram notifications
    
    # Settings
    is_active = Column(Boolean, default=True)
    email_notifications = Column(Boolean, default=True)
    telegram_notifications = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<User {self.username}>"
