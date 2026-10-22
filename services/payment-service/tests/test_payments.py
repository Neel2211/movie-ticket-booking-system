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

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    """Create fresh tables before each test and clean them up after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_create_payment_success():
    """Test successful payment creation (POST /api/v1/payments)."""
    payload = {
        "booking_id": 301,
        "amount": 550.00,
        "currency": "INR"
    }
    headers = {"Idempotency-Key": "key-create-301"}
    
    response = client.post("/api/v1/payments", json=payload, headers=headers)
    
    assert response.status_code == 201
    data = response.json()
    assert data["booking_id"] == 301
    assert data["amount"] == 550.00
    assert data["status"] == "SUCCESS"
    assert "gateway_transaction_id" in data


def test_create_payment_missing_idempotency_header():
    """Test validation failure when missing the required Idempotency-Key header."""
    payload = {
        "booking_id": 302,
        "amount": 250.00,
        "currency": "INR"
    }
    # No headers provided
    response = client.post("/api/v1/payments", json=payload)
    
    # Expecting 422 Unprocessable Entity due to missing required header
    assert response.status_code == 422


def test_create_payment_invalid_amount():
    """Test validation failure when amount is negative or invalid."""
    payload = {
        "booking_id": 303,
        "amount": -50.00,  # Invalid amount
        "currency": "INR"
    }
    headers = {"Idempotency-Key": "key-invalid-amount"}
    
    response = client.post("/api/v1/payments", json=payload, headers=headers)
    assert response.status_code == 422


def test_payment_idempotency():
    """Test Challenge 2: Duplicate requests with same Idempotency-Key return cached records."""
    payload = {
        "booking_id": 304,
        "amount": 400.00,
        "currency": "INR"
    }
    headers = {"Idempotency-Key": "idempotent-key-repeat-test"}
    
    # First request
    res1 = client.post("/api/v1/payments", json=payload, headers=headers)
    assert res1.status_code == 201
    id1 = res1.json()["id"]
    txn1 = res1.json()["gateway_transaction_id"]

    # Second request with same key
    res2 = client.post("/api/v1/payments", json=payload, headers=headers)
    assert res2.status_code in (200, 201)
    id2 = res2.json()["id"]
    txn2 = res2.json()["gateway_transaction_id"]

    # Verify identical cached response returned
    assert id1 == id2
    assert txn1 == txn2


def test_get_payment_by_id_success():
    """Test fetching an individual payment record by its ID."""
    payload = {
        "booking_id": 305,
        "amount": 900.00,
        "currency": "INR"
    }
    headers = {"Idempotency-Key": "key-get-test"}
    
    create_res = client.post("/api/v1/payments", json=payload, headers=headers)
    payment_id = create_res.json()["id"]

    # Fetch payment record
    get_res = client.get(f"/api/v1/payments/{payment_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == payment_id
    assert get_res.json()["booking_id"] == 305


def test_get_payment_not_found():
    """Test 404 response when fetching a non-existent payment ID."""
    response = client.get("/api/v1/payments/99999")
    assert response.status_code == 404


def test_saga_compensation_refund():
    """Test Challenge 3: SAGA Rollback / Refund endpoint updates status to REFUNDED."""
    payload = {
        "booking_id": 306,
        "amount": 1200.00,
        "currency": "INR"
    }
    headers = {"Idempotency-Key": "saga-refund-key-01"}
    
    # Create payment
    create_res = client.post("/api/v1/payments", json=payload, headers=headers)
    payment_id = create_res.json()["id"]
    assert create_res.json()["status"] == "SUCCESS"

    # Trigger Refund / SAGA compensation
    refund_res = client.post(f"/api/v1/payments/{payment_id}/refund")
    assert refund_res.status_code == 200
    
    refund_data = refund_res.json()
    assert refund_data["payment_id"] == payment_id
    assert refund_data["status"] == "REFUNDED"