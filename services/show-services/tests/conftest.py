
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from app.database import Base, make_session_factory
from app.main import create_app
from app.models import Show, Seat


@pytest.fixture
def client(tmp_path):
    # Create an isolated SQLite database for each test
    database_file = tmp_path / "test_show.db"
    database_url = f"sqlite:///{database_file.as_posix()}"

    # Create a SQLAlchemy Engine
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
    )

    # Create the tables using the Engine, not the database URL string
    Base.metadata.create_all(bind=engine)

    # Create a session factory bound to the Engine
    SessionLocal = make_session_factory(engine)

    # Initialize the test data
    with SessionLocal() as db:
        show = Show(
            show_id=1,
            movie_name="Test Movie",
            show_time="2026-11-01T18:00:00",
        )
        db.add(show)

        # Insert the parent record before its related seats
        db.flush()

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

    # Create the FastAPI app and test client
    app = create_app(database_url=database_url)

    with TestClient(app) as test_client:
        yield test_client

    # Clean up the test database connections
    app_engine = getattr(app.state, "engine", None)
    if app_engine is not None:
        app_engine.dispose()

    Base.metadata.drop_all(bind=engine)
    engine.dispose()
