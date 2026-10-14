"""Request/response schemas (BR-U2: input validation)."""
import re
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

PHONE_RE = re.compile(r"^\+?[0-9]{10,15}$")


class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


def _clean_phone(v: str) -> str:
    v = re.sub(r"[\s-]", "", v)
    if not PHONE_RE.match(v):
        raise ValueError("phone must be 10-15 digits, optionally starting with '+'")
    return v


def _clean_name(v):
    if v is None:
        return v
    v = v.strip()
    if len(v) < 2:
        raise ValueError("name must have at least 2 non-space characters")
    return v


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100, examples=["Yamuna"])
    email: EmailStr = Field(examples=["yamuna@example.com"])
    phone: str = Field(examples=["+919876543210"])

    _name = field_validator("name")(classmethod(lambda cls, v: _clean_name(v)))
    _phone = field_validator("phone")(classmethod(lambda cls, v: _clean_phone(v)))


class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

    _name = field_validator("name")(classmethod(lambda cls, v: _clean_name(v)))
    _phone = field_validator("phone")(classmethod(lambda cls, v: None if v is None else _clean_phone(v)))


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: str
    phone: str
    status: UserStatus
    created_at: datetime
    updated_at: datetime


class UserList(BaseModel):
    items: list[UserOut]
    total: int
    limit: int
    offset: int


class ErrorBody(BaseModel):
    code: str
    message: str
    details: list = []
    request_id: str


class ErrorResponse(BaseModel):
    error: ErrorBody
