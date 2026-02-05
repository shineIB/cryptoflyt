"""
Pydantic schemas for User API.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    username: str


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    email: EmailStr
    username: str
    password: str


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    username: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    email_notifications: Optional[bool] = None
    telegram_notifications: Optional[bool] = None


class UserResponse(BaseModel):
    """Schema for user response."""
    id: int
    email: str
    username: str
    telegram_chat_id: Optional[str]
    email_notifications: bool
    telegram_notifications: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for auth token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
