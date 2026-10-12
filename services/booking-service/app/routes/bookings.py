from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Booking, Seat, PaymentRequest
from app.schemas import (
    BookingCreate,
    BookingResponse,
    BookingStatusUpdate,
    BookingProcessRequest,
    PaymentRequestSchema
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

@router.post("/bookings/{booking_id}/process")
def process_booking(
    booking_id: int,
    request: BookingProcessRequest,
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

    if booking.status != "PENDING":
        raise HTTPException(
            status_code=400,
            detail="Booking must be in PENDING state"
        )

    # Simulate seat reservation
    booking.status = "RESERVED"
    db.commit()

    # Simulate payment processing
    if request.payment_success:
        booking.status = "CONFIRMED"
    else:
        booking.status = "PAYMENT_FAILED"
        db.commit()

        # Saga compensation
        booking.status = "CANCELLED"

    db.commit()
    db.refresh(booking)

    return {
        "booking_id": booking.booking_id,
        "final_status": booking.status
    }

@router.post("/reserve-seat")
def reserve_seat(
    show_id: int,
    seat_number: str,
    db: Session = Depends(get_db)
):
    seat = (
        db.query(Seat)
        .filter(
            Seat.show_id == show_id,
            Seat.seat_number == seat_number
        )
        .first()
    )

    if seat.status != "AVAILABLE":
        raise HTTPException(
            status_code=400,
            detail="Seat already reserved"
        )

    seat.status = "RESERVED"

    db.commit()

    return {
        "message": "Seat reserved"
    }

@router.post("/payments")
def process_payment(
    request: PaymentRequestSchema,
    db: Session = Depends(get_db)
):
    existing = (
        db.query(PaymentRequest)
        .filter(
            PaymentRequest.idempotency_key ==
            request.idempotency_key
        )
        .first()
    )

    if existing:
        return {
            "message": "Duplicate request",
            "idempotency_key": request.idempotency_key
        }

    payment = PaymentRequest(
        idempotency_key=request.idempotency_key,
        status="SUCCESS"
    )

    db.add(payment)
    db.commit()

    return {
        "message": "Payment processed",
        "idempotency_key": request.idempotency_key
    }