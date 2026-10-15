from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PaymentCreateRequest(BaseModel):
    booking_id: int = Field(..., description="ID of the booking being paid for")
    amount: float = Field(..., gt=0, description="Payment amount")
    currency: str = Field(default="INR", description="Currency code")

class PaymentResponse(BaseModel):
    id: int
    booking_id: int
    amount: float
    currency: str
    status: str
    gateway_transaction_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True