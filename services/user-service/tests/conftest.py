import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


@pytest.fixture
def client(tmp_path):
    settings = Settings("user-service-test", 8001, f"sqlite:///{tmp_path/'test.db'}", "WARNING")
    with TestClient(create_app(settings)) as c:
        yield c


@pytest.fixture
def make_user(client):
    counter = {"n": 0}

    def _make(**overrides):
        counter["n"] += 1
        body = {"name": "Test User", "email": f"user{counter['n']}@example.com", "phone": "+919876543210"}
        body.update(overrides)
        return client.post("/api/v1/users", json=body)

    return _make
