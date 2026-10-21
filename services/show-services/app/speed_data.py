from sqlalchemy import select

from app.database import (
    Base,
    get_database_url,
    make_engine,
    make_session_factory,
)
from app.models import Seat, Show


def seed():
    engine = make_engine(get_database_url())
    Base.metadata.create_all(engine)
    SessionLocal = make_session_factory(engine)

    with SessionLocal() as db:
        show = db.scalar(
            select(Show).where(Show.show_id == 1)
        )

        if show is None:
            show = Show(
                show_id=1,
                movie_name="Demo Movie",
                show_time="2026-11-01T18:00:00",
            )
            db.add(show)
            db.flush()

        for seat_number in ["A1", "A2", "A3", "A4", "A5"]:
            seat = db.scalar(
                select(Seat).where(
                    Seat.show_id == show.show_id,
                    Seat.seat_number == seat_number,
                )
            )

            if seat is None:
                db.add(
                    Seat(
                        show_id=show.show_id,
                        seat_number=seat_number,
                        status="AVAILABLE",
                    )
                )

        db.commit()

    engine.dispose()
    print("Show Service sample data is ready.")


if __name__ == "__main__":
    seed()