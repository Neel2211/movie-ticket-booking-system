
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import select

from app.models import Seat
from app.database import make_session_factory


def test_get_shows(client):
    response = client.get("/shows")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["movie_name"] == "Test Movie"


def test_reserve_available_seat(client):
    response = client.post(
        "/seats/reserve",
        json={"show_id": 1, "seat_number": "A1"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "RESERVED"


def test_cannot_reserve_same_seat_twice(client):
    payload = {"show_id": 1, "seat_number": "A1"}

    first = client.post("/seats/reserve", json=payload)
    second = client.post("/seats/reserve", json=payload)

    assert first.status_code == 200
    assert second.status_code == 409


def test_cannot_reserve_nonexistent_seat(client):
    response = client.post(
        "/seats/reserve",
        json={"show_id": 1, "seat_number": "Z99"},
    )

    assert response.status_code == 404


def test_release_reserved_seat(client):
    payload = {"show_id": 1, "seat_number": "A1"}

    reserve = client.post("/seats/reserve", json=payload)
    release = client.post("/seats/release", json=payload)

    assert reserve.status_code == 200
    assert release.status_code == 200
    assert release.json()["status"] == "AVAILABLE"


def test_cannot_release_available_seat(client):
    response = client.post(
        "/seats/release",
        json={"show_id": 1, "seat_number": "A1"},
    )

    assert response.status_code == 409


def test_twenty_concurrent_reservations(client):
    payload = {"show_id": 1, "seat_number": "A1"}

    def reserve_once(_):
        return client.post("/seats/reserve", json=payload)

    with ThreadPoolExecutor(max_workers=20) as executor:
        responses = list(executor.map(reserve_once, range(20)))

    success_count = sum(
        response.status_code == 200
        for response in responses
    )
    conflict_count = sum(
        response.status_code == 409
        for response in responses
    )

    assert success_count == 1
    assert conflict_count == 19

    with make_session_factory(client.app.state.engine)() as db:
        seat = db.scalar(
            select(Seat).where(
                Seat.show_id == 1,
                Seat.seat_number == "A1",
            )
        )

        assert seat is not None
        assert seat.status == "RESERVED"
