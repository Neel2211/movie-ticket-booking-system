from fastapi import FastAPI
from app.database import Base, engine
from app.routes.bookings import router
Base.metadata.create_all(bind=engine)
from app.database import SessionLocal
from app.models import Seat

db = SessionLocal()

existing_seat = (
    db.query(Seat)
    .filter(
        Seat.show_id == 1,
        Seat.seat_number == "A1"
    )
    .first()
)

if not existing_seat:
    seat = Seat(
        show_id=1,
        seat_number="A1",
        status="AVAILABLE"
    )
    db.add(seat)
    db.commit()

db.close()
app = FastAPI(title="Booking Service")
app.include_router(router)
@app.get("/")
def home():
	return {"message": "Booking Service Running"}
