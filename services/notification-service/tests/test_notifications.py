import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

# Use an in-memory SQLite database for fast, isolated testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override FastAPI's database dependency with the test database
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    """Create fresh tables before each test and clean them up after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_send_notification_success():
    """Test successful notification dispatch (POST /api/v1/notifications)."""
    payload = {
        "recipient": "naveen@example.com",
        "channel": "EMAIL",
        "template_id": "booking_confirmation",
        "message": "Your booking ID 103 for Inception is confirmed!",
        "payload": {
            "booking_id": 103,
            "movie_title": "Inception",
            "showtime": "2026-10-25T18:30:00"
        }
    }
    
    response = client.post("/api/v1/notifications", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["recipient"] == "naveen@example.com"
    assert data["channel"] == "EMAIL"
    assert "id" in data


def test_send_notification_missing_message():
    """Test validation error (422) when required fields like 'message' are missing."""
    payload = {
        "recipient": "naveen@example.com",
        "channel": "EMAIL",
        "template_id": "booking_confirmation"
        # Missing "message" field
    }
    
    response = client.post("/api/v1/notifications", json=payload)
    assert response.status_code == 422


def test_get_notification_by_id_success():
    """Test fetching an individual notification log by its ID."""
    payload = {
        "recipient": "test@example.com",
        "channel": "SMS",
        "template_id": "reminder",
        "message": "Your movie starts in 1 hour."
    }
    
    create_res = client.post("/api/v1/notifications", json=payload)
    assert create_res.status_code == 201
    notif_id = create_res.json()["id"]

    # Fetch notification status
    get_res = client.get(f"/api/v1/notifications/{notif_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == notif_id
    assert get_res.json()["channel"] == "SMS"


def test_get_notification_not_found():
    """Test 404 response when fetching a non-existent notification ID."""
    response = client.get("/api/v1/notifications/99999")
    assert response.status_code == 404


def test_health_check():
    """Test service health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200