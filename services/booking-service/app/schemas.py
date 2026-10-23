from pydantic import BaseModel


class BookingCreate(BaseModel):
    user_id: str
    show_id: int
    seat_number: str

class BookingResponse(BaseModel):
    booking_id: int
    user_id: str
    show_id: int
    seat_number: str
    status: str

    class Config:
        from_attributes = True

class BookingStatusUpdate(BaseModel):
    status: str

class BookingProcessRequest(BaseModel):
    payment_success: bool

class PaymentRequestSchema(BaseModel):
    idempotency_key: str