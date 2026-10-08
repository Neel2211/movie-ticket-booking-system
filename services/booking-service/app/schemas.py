from pydantic import BaseModel
class BookingCreate(BaseModel):
	user_id: int
	show_id: int
	seat_number: str
class BookingResponse(BaseModel):
	booking_id: int
	user_id: int
	show_id: int
	seat_number: str
	status: str
	class Config:
    	from_attributes = True
