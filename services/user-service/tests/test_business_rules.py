"""One test per business rule (traceability: BR-U1..BR-U4 -> code in app/service.py, app/schemas.py)."""
import pytest

from app.errors import InvalidStateTransitionError
from app.service import check_transition


# ---- BR-U1: email unique, case-insensitive --------------------------------
def test_br_u1_duplicate_email_rejected_case_insensitive(make_user):
    assert make_user(email="a@example.com").status_code == 201
    r = make_user(email="A@Example.COM")
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "EMAIL_ALREADY_EXISTS"


def test_br_u1_concurrent_same_email_exactly_one_wins(client):
    from concurrent.futures import ThreadPoolExecutor
    body = {"name": "Racer", "email": "race@example.com", "phone": "+919876543210"}
    with ThreadPoolExecutor(max_workers=20) as pool:
        codes = list(pool.map(lambda _: client.post("/api/v1/users", json=body).status_code, range(20)))
    assert codes.count(201) == 1
    assert codes.count(409) == 19
    assert client.get("/api/v1/users", params={"limit": 100}).json()["total"] == 1


# ---- BR-U2: input validation ------------------------------------------------
@pytest.mark.parametrize("override", [
    {"email": "not-an-email"},
    {"phone": "12345"},
    {"phone": "abcdefghijk"},
    {"name": " "},
    {"name": "x"},
])
def test_br_u2_invalid_input_rejected(make_user, override):
    r = make_user(**override)
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "VALIDATION_ERROR"


def test_br_u2_phone_is_normalised(make_user):
    r = make_user(phone="+91 98765-43210")
    assert r.status_code == 201
    assert r.json()["phone"] == "+919876543210"


# ---- BR-U3: status lifecycle -------------------------------------------------
def test_br_u3_transition_rules_pure():
    check_transition("ACTIVE", "INACTIVE")
    check_transition("INACTIVE", "ACTIVE")
    with pytest.raises(InvalidStateTransitionError):
        check_transition("ACTIVE", "ACTIVE")
    with pytest.raises(InvalidStateTransitionError):
        check_transition("INACTIVE", "INACTIVE")


def test_br_u3_lifecycle_via_api(client, make_user):
    uid = make_user().json()["id"]
    assert client.post(f"/api/v1/users/{uid}/activate").status_code == 409  # already ACTIVE
    r = client.post(f"/api/v1/users/{uid}/deactivate")
    assert r.status_code == 200 and r.json()["status"] == "INACTIVE"
    assert client.post(f"/api/v1/users/{uid}/deactivate").status_code == 409
    r = client.post(f"/api/v1/users/{uid}/activate")
    assert r.status_code == 200 and r.json()["status"] == "ACTIVE"


# ---- BR-U4: inactive users cannot be edited ---------------------------------
def test_br_u4_inactive_user_cannot_be_edited(client, make_user):
    uid = make_user().json()["id"]
    client.post(f"/api/v1/users/{uid}/deactivate")
    r = client.put(f"/api/v1/users/{uid}", json={"name": "New Name"})
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "USER_INACTIVE"
