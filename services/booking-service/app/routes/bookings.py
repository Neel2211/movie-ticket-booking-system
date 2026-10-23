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
import requests
from app.clients import (
    fetch_user,
    reserve_seat_remote,
    release_seat_remote,
    charge_payment,
    send_notification,
    TICKET_PRICE
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
    # Integration: only an ACTIVE user known to User Service may book
    try:
        user = fetch_user(booking.user_id)
    except requests.RequestException:
        raise HTTPException(
            status_code=503,
            detail="User Service unavailable"
        )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.get("status") != "ACTIVE":
        raise HTTPException(
            status_code=409,
            detail="User is not ACTIVE"
        )
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

    # Step 1 - reserve the seat in Show Service (it owns seat inventory)
    try:
        seat_http_status = reserve_seat_remote(
            booking.show_id,
            booking.seat_number
        )
    except requests.RequestException:
        raise HTTPException(
            status_code=503,
            detail="Show Service unavailable"
        )

    if seat_http_status in (404, 409):
        booking.status = "CANCELLED"
        db.commit()
        raise HTTPException(
            status_code=seat_http_status,
            detail=(
                "Seat not found for this show"
                if seat_http_status == 404
                else "Seat is not available for reservation"
            )
        )

    if seat_http_status != 200:
        raise HTTPException(
            status_code=503,
            detail=f"Show Service returned HTTP {seat_http_status}"
        )

    booking.status = "RESERVED"
    db.commit()

    # Step 2 - charge via Payment Service (idempotent per booking).
    # payment_success=False is the demo switch for a declined payment:
    # it sends amount 0, which Payment Service rejects.
    payment_ok = charge_payment(
        booking.booking_id,
        f"booking-{booking.booking_id}-{int(booking.created_at.timestamp())}",
        TICKET_PRICE if request.payment_success else 0
    )

    if payment_ok:
        booking.status = "CONFIRMED"
    else:
        booking.status = "PAYMENT_FAILED"
        db.commit()

        # Saga compensation: give the seat back to Show Service
        release_seat_remote(booking.show_id, booking.seat_number)
        booking.status = "CANCELLED"

    db.commit()
    db.refresh(booking)

    # Step 3 - notify the user (best effort, never fails the booking)
    user_email = None
    try:
        user = fetch_user(booking.user_id)
        if user:
            user_email = user.get("email")
    except requests.RequestException:
        pass

    if user_email:
        if booking.status == "CONFIRMED":
            send_notification(
                user_email,
                "Booking confirmed",
                f"Booking #{booking.booking_id} for show {booking.show_id}, "
                f"seat {booking.seat_number} is confirmed."
            )
        else:
            send_notification(
                user_email,
                "Booking cancelled",
                f"Booking #{booking.booking_id} for show {booking.show_id}, "
                f"seat {booking.seat_number} was cancelled because payment failed."
            )

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