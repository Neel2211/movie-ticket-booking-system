from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.database import Base

class PaymentModel(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    booking_id = Column(Integer, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    status = Column(String, default="PENDING")  # PENDING, SUCCESS, FAILED
    gateway_transaction_id = Column(String, nullable=True)
    idempotency_key = Column(String, unique=True, index=True, nullable=False)
    response_payload = Column(String, nullable=True) # Cached response for idempotent replays
    created_at = Column(DateTime, default=datetime.utcnow)