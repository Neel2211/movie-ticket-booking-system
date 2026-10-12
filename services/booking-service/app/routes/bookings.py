from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Booking
from app.schemas import (
    BookingCreate,
    BookingResponse,
    BookingStatusUpdate
)

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

@router.put("/bookings/{booking_id}/status")
def update_booking_status(
    booking_id: int,
    status_update: BookingStatusUpdate,
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

    allowed_transitions = {
        "PENDING": ["RESERVED"],
        "RESERVED": ["CONFIRMED", "PAYMENT_FAILED"],
        "PAYMENT_FAILED": ["CANCELLED"],
        "CONFIRMED": [],
        "CANCELLED": []
    }

    current_status = booking.status
    new_status = status_update.status

    if new_status not in allowed_transitions.get(current_status, []):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transition from {current_status} to {new_status}"
        )

    booking.status = new_status

    db.commit()
    db.refresh(booking)

    return {
        "booking_id": booking.booking_id,
        "status": booking.status
    }

