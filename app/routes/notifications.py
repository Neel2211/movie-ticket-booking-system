from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import NotificationModel
from app.schemas import NotificationCreateRequest, NotificationResponse

router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])

@router.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def send_notification(payload: NotificationCreateRequest, db: Session = Depends(get_db)):
    # Simulate mock notification provider delivery logic (Condition 1e)
    # You can introduce transient faults or delays here if testing resilience (Challenge 3A)
    delivery_status = "SENT"
    if not payload.recipient or not payload.message:
        delivery_status = "FAILED"

    new_notification = NotificationModel(
        recipient=payload.recipient,
        channel=payload.channel.upper(),
        subject=payload.subject,
        message=payload.message,
        status=delivery_status
    )

    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)

    return new_notification

@router.get("", response_model=List[NotificationResponse])
def list_notifications(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    notifications = db.query(NotificationModel).offset(skip).limit(limit).all()
    return notifications

@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(notification_id: int, db: Session = Depends(get_db)):
    notification = db.query(NotificationModel).filter(NotificationModel.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification record not found")
    return notification