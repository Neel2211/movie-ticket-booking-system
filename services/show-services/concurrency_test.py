from concurrent.futures import ThreadPoolExecutor
from collections import Counter

import httpx
from sqlalchemy import select

from app.database import get_database_url, make_engine, make_session_factory
from app.models import Seat

BASE_URL = "http://127.0.0.1:8002"
SHOW_ID = 1
SEAT_NUMBER = "A1"
REQUEST_COUNT = 20


def reserve_once(_):
    try:
        response = httpx.post(
            f"{BASE_URL}/seats/reserve",
            json={
                "show_id": SHOW_ID,
                "seat_number": SEAT_NUMBER,
            },
            timeout=15,
        )
        return response.status_code
    except httpx.HTTPError as exc:
        print(f"Request error: {exc}")
        return None


def main():
    # Reset this demonstration seat if a previous run left it RESERVED.
    # Use only with the local demo database and a dedicated demo seat.
    httpx.post(
        f"{BASE_URL}/seats/release",
        json={
            "show_id": SHOW_ID,
            "seat_number": SEAT_NUMBER,
        },
        timeout=15,
    )

    with ThreadPoolExecutor(max_workers=REQUEST_COUNT) as executor:
        results = list(executor.map(reserve_once, range(REQUEST_COUNT)))

    counts = Counter(results)
    print("HTTP status counts:", dict(counts))

    engine = make_engine(get_database_url())
    SessionLocal = make_session_factory(engine)

    with SessionLocal() as db:
        seat = db.scalar(
            select(Seat).where(
                Seat.show_id == SHOW_ID,
                Seat.seat_number == SEAT_NUMBER,
            )
        )

        print(
            "Final seat state:",
            seat.status if seat else "NOT FOUND",
        )

    engine.dispose()

    assert counts[200] == 1, "Expected exactly one successful reservation"
    assert counts[409] == 19, "Expected 19 conflict responses"
    assert counts[None] == 0, "Unexpected request failures"
    assert seat is not None and seat.status == "RESERVED"

    print("PASS: No seat over-allocation detected.")


if __name__ == "__main__":
    main()