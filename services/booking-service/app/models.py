from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base
class Booking(Base):
	__tablename__ = "bookings"
	booking_id = Column(Integer, primary_key=True, index=True)
	user_id = Column(String, nullable=False)
	show_id = Column(Integer, nullable=False)
	seat_number = Column(String, nullable=False)
	status = Column(String, nullable=False, default="PENDING")
	created_at = Column(DateTime, default=datetime.utcnow)

class Seat(Base):
    __tablename__ = "seats"

    seat_id = Column(Integer, primary_key=True, index=True)
    show_id = Column(Integer, nullable=False)
    seat_number = Column(String, nullable=False)
    status = Column(String, nullable=False, default="AVAILABLE")

class PaymentRequest(Base):
    __tablename__ = "payment_requests"

    id = Column(Integer, primary_key=True, index=True)
    idempotency_key = Column(String, unique=True, nullable=False)
    status = Column(String, nullable=False)