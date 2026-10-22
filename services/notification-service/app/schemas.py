from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class NotificationCreateRequest(BaseModel):
    recipient: str = Field(..., description="Target email or phone number")
    channel: str = Field(default="EMAIL", description="Delivery channel: EMAIL or SMS")
    subject: Optional[str] = Field(None, description="Subject line for email notifications")
    message: str = Field(..., description="Content of the notification message")

class NotificationResponse(BaseModel):
    id: int
    recipient: str
    channel: str
    subject: Optional[str] = None
    message: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True