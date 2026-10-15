def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_create_and_get(client, make_user):
    created = make_user(name="Yamuna").json()
    assert created["status"] == "ACTIVE"
    r = client.get(f"/api/v1/users/{created['id']}")
    assert r.status_code == 200 and r.json()["name"] == "Yamuna"


def test_get_unknown_user_uses_standard_error_format(client):
    r = client.get("/api/v1/users/does-not-exist")
    assert r.status_code == 404
    err = r.json()["error"]
    assert err["code"] == "USER_NOT_FOUND" and err["request_id"]


def test_unknown_route_uses_standard_error_format(client):
    r = client.get("/api/v1/nope")
    assert r.status_code == 404 and r.json()["error"]["code"] == "NOT_FOUND"


def test_update_profile(client, make_user):
    uid = make_user().json()["id"]
    r = client.put(f"/api/v1/users/{uid}", json={"name": "Renamed", "phone": "9876543211"})
    assert r.status_code == 200
    assert r.json()["name"] == "Renamed" and r.json()["phone"] == "9876543211"


def test_update_to_taken_email_conflicts(client, make_user):
    make_user(email="taken@example.com")
    uid = make_user().json()["id"]
    r = client.put(f"/api/v1/users/{uid}", json={"email": "Taken@example.com"})
    assert r.status_code == 409


def test_list_pagination_and_status_filter(client, make_user):
    ids = [make_user().json()["id"] for _ in range(3)]
    client.post(f"/api/v1/users/{ids[0]}/deactivate")
    page = client.get("/api/v1/users", params={"limit": 2}).json()
    assert page["total"] == 3 and len(page["items"]) == 2
    inactive = client.get("/api/v1/users", params={"status": "INACTIVE"}).json()
    assert inactive["total"] == 1
    assert client.get("/api/v1/users", params={"limit": 0}).status_code == 422


def test_correlation_id_is_echoed_or_generated(client):
    assert client.get("/health", headers={"X-Request-ID": "abc-123"}).headers["X-Request-ID"] == "abc-123"
    assert client.get("/health").headers["X-Request-ID"]


def test_contract_alias_paths_without_prefix(client):
    """Team contract: POST /users and GET /users/{id} must also work."""
    r = client.post("/users", json={"name": "Alias User", "email": "alias@example.com", "phone": "+919876543210"})
    assert r.status_code == 201
    uid = r.json()["id"]
    assert client.get(f"/users/{uid}").status_code == 200
    assert client.get(f"/api/v1/users/{uid}").status_code == 200  # same data on the versioned path
    assert client.get("/users/missing").status_code == 404