"""
Alert management API routes.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.alert import Alert
from app.models.price import AlertHistory
from app.schemas.alert import AlertCreate, AlertUpdate, AlertResponse, AlertHistoryResponse
from app.config import settings

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=List[AlertResponse])
async def get_alerts(
    active_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all alerts for the current user.
    """
    query = db.query(Alert).filter(Alert.user_id == current_user.id)
    
    if active_only:
        query = query.filter(Alert.is_active == True)
    
    alerts = query.order_by(Alert.created_at.desc()).all()
    return [AlertResponse.model_validate(a) for a in alerts]


@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_data: AlertCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new price alert.
    """
    # Validate symbol
    if alert_data.symbol not in settings.supported_symbols:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported symbol. Supported: {', '.join(settings.supported_symbols)}"
        )
    
    # Check alert limit (e.g., max 20 active alerts per user)
    active_count = db.query(Alert).filter(
        Alert.user_id == current_user.id,
        Alert.is_active == True
    ).count()
    
    if active_count >= 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum active alerts limit reached (20)"
        )
    
    # Create alert
    alert = Alert(
        user_id=current_user.id,
        symbol=alert_data.symbol,
        target_price=alert_data.target_price,
        condition=alert_data.condition,
        note=alert_data.note,
        notify_telegram=alert_data.notify_telegram,
        notify_email=alert_data.notify_email
    )
    
    db.add(alert)
    db.commit()
    db.refresh(alert)
    
    return AlertResponse.model_validate(alert)


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific alert by ID.
    """
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    return AlertResponse.model_validate(alert)


@router.patch("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: int,
    alert_data: AlertUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing alert.
    """
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    # Update fields
    if alert_data.target_price is not None:
        alert.target_price = alert_data.target_price
    if alert_data.condition is not None:
        alert.condition = alert_data.condition
    if alert_data.is_active is not None:
        alert.is_active = alert_data.is_active
        # Reset triggered status if reactivating
        if alert_data.is_active:
            alert.is_triggered = False
            alert.triggered_at = None
            alert.triggered_price = None
    if alert_data.note is not None:
        alert.note = alert_data.note
    if alert_data.notify_telegram is not None:
        alert.notify_telegram = alert_data.notify_telegram
    if alert_data.notify_email is not None:
        alert.notify_email = alert_data.notify_email
    
    db.commit()
    db.refresh(alert)
    
    return AlertResponse.model_validate(alert)


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an alert.
    """
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    db.delete(alert)
    db.commit()


@router.get("/history/all", response_model=List[AlertHistoryResponse])
async def get_alert_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get history of triggered alerts.
    """
    history = db.query(AlertHistory).filter(
        AlertHistory.user_id == current_user.id
    ).order_by(AlertHistory.triggered_at.desc()).limit(limit).all()
    
    return [AlertHistoryResponse.model_validate(h) for h in history]
