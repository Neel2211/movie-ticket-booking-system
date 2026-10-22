from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base

class NotificationModel(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    recipient = Column(String, nullable=False) # Email address or Phone number
    channel = Column(String, default="EMAIL")   # EMAIL or SMS
    subject = Column(String, nullable=True)
    message = Column(String, nullable=False)
    status = Column(String, default="SENT")     # SENT, FAILED
    created_at = Column(DateTime, default=datetime.utcnow)