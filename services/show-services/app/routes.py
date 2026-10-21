from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models import Seat, Show
from app.schemas import (
    SeatOperationResponse,
    SeatReleaseRequest,
    SeatReserveRequest,
    ShowOut,
)

router = APIRouter()


def get_db(request: Request):
    """Provide one database session per request."""
    session_factory = request.app.state.session_factory
    db = session_factory()

    try:
        yield db
    finally:
        db.close()


@router.get("/shows", response_model=list[ShowOut])
def get_shows(db: Session = Depends(get_db)):
    """Return the shows stored in the Show Service database."""
    statement = select(Show).order_by(Show.show_id)
    return db.scalars(statement).all()


@router.post(
    "/seats/reserve",
    response_model=SeatOperationResponse,
)
def reserve_seat(
    request_data: SeatReserveRequest,
    db: Session = Depends(get_db),
):
    """
    Reserve a seat only if its current status is AVAILABLE.
    The status check and update happen in one SQL statement.
    """
    statement = (
        update(Seat)
        .where(
            Seat.show_id == request_data.show_id,
            Seat.seat_number == request_data.seat_number,
            Seat.status == "AVAILABLE",
        )
        .values(status="RESERVED")
        .execution_options(synchronize_session=False)
    )

    result = db.execute(statement)

    if result.rowcount != 1:
        db.rollback()

        seat = db.scalar(
            select(Seat).where(
                Seat.show_id == request_data.show_id,
                Seat.seat_number == request_data.seat_number,
            )
        )

        if seat is None:
            raise HTTPException(
                status_code=404,
                detail="Seat not found for this show",
            )

        raise HTTPException(
            status_code=409,
            detail="Seat is not available for reservation",
        )

    db.commit()

    return {
        "success": True,
        "show_id": request_data.show_id,
        "seat_number": request_data.seat_number,
        "status": "RESERVED",
    }


@router.post(
    "/seats/release",
    response_model=SeatOperationResponse,
)
def release_seat(
    request_data: SeatReleaseRequest,
    db: Session = Depends(get_db),
):
    """
    Release only a currently RESERVED seat.
    Never release a BOOKED seat through this endpoint.
    """
    statement = (
        update(Seat)
        .where(
            Seat.show_id == request_data.show_id,
            Seat.seat_number == request_data.seat_number,
            Seat.status == "RESERVED",
        )
        .values(status="AVAILABLE")
        .execution_options(synchronize_session=False)
    )

    result = db.execute(statement)

    if result.rowcount != 1:
        db.rollback()

        seat = db.scalar(
            select(Seat).where(
                Seat.show_id == request_data.show_id,
                Seat.seat_number == request_data.seat_number,
            )
        )

        if seat is None:
            raise HTTPException(
                status_code=404,
                detail="Seat not found for this show",
            )

        raise HTTPException(
            status_code=409,
            detail="Only a RESERVED seat can be released",
        )

    db.commit()

    return {
        "success": True,
        "show_id": request_data.show_id,
        "seat_number": request_data.seat_number,
        "status": "AVAILABLE",
    }