from fastapi import FastAPI
from app.database import Base, engine
from app.routes.bookings import router
Base.metadata.create_all(bind=engine)
app = FastAPI(title="Booking Service")
app.include_router(router)
@app.get("/")
def home():
	return {"message": "Booking Service Running"}
