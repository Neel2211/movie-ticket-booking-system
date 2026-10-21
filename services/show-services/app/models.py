from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Show(Base):
    __tablename__ = "shows"

    show_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    movie_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    show_time: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )


class Seat(Base):
    __tablename__ = "seats"

    __table_args__ = (
        UniqueConstraint(
            "show_id",
            "seat_number",
            name="uq_seat_per_show",
        ),
        CheckConstraint(
            "status IN ('AVAILABLE', 'RESERVED', 'BOOKED')",
            name="ck_seat_status",
        ),
    )

    seat_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    show_id: Mapped[int] = mapped_column(
        ForeignKey("shows.show_id"),
        nullable=False,
        index=True,
    )
    seat_number: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="AVAILABLE",
    )