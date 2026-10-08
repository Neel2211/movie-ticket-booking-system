from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Booking
from app.schemas import BookingCreate, BookingResponse

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/health")
def health():
    return {"status": "Booking Service Healthy"}


@router.post("/bookings", response_model=BookingResponse)
def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    new_booking = Booking(
        user_id=booking.user_id,
        show_id=booking.show_id,
        seat_number=booking.seat_number,
        status="PENDING",
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking

from fastapi import HTTPException

@router.get("/bookings/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db)
):
    booking = (
        db.query(Booking)
        .filter(Booking.booking_id == booking_id)
        .first()
    )
    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )
    return booking



