from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ShowOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    show_id: int
    movie_name: str
    show_time: str


class SeatReserveRequest(BaseModel):
    show_id: int = Field(gt=0)
    seat_number: str = Field(min_length=1, max_length=20)


class SeatReleaseRequest(BaseModel):
    show_id: int = Field(gt=0)
    seat_number: str = Field(min_length=1, max_length=20)


class SeatOperationResponse(BaseModel):
    success: bool
    show_id: int
    seat_number: str
    status: Literal["AVAILABLE", "RESERVED", "BOOKED"]