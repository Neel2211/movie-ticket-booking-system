import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.database import make_session_factory
from app.main import create_app
from app.models import Seat, Show


@pytest.fixture
def client(tmp_path):
    database_file = tmp_path / "test_show.db"
    database_url = f"sqlite:///{database_file.as_posix()}"

    app = create_app(database_url)

    SessionLocal = app.state.session_factory

    with SessionLocal() as db:
        db.add(
            Show(
                show_id=1,
                movie_name="Test Movie",
                show_time="2026-11-01T18:00:00",
            )
        )

        db.add_all(
            [
                Seat(
                    show_id=1,
                    seat_number="A1",
                    status="AVAILABLE",
                ),
                Seat(
                    show_id=1,
                    seat_number="A2",
                    status="AVAILABLE",
                ),
            ]
        )

        db.commit()

    with TestClient(app) as test_client:
        yield test_client

    app.state.engine.dispose()


def get_session(client):
    return make_session_factory(
        client.app.state.engine
    )()