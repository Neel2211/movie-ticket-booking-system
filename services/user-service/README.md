# User Service (port 8001)

Owner: Yamuna. Part of the Movie Ticket Booking System (Scalable Services, Group 9).

**Responsibility (one sentence):** owns user profiles and their ACTIVE/INACTIVE status; other services keep only the `user_id`.

## Run

```bash
cd services/user-service
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                   # optional; defaults are the same
python -m uvicorn app.main:app --port 8001
```

Swagger UI: http://localhost:8001/docs | OpenAPI JSON: http://localhost:8001/openapi.json

## Environment variables

| Variable | Default | Meaning |
|---|---|---|
| `SERVICE_NAME` | `user-service` | name in logs / health |
| `PORT` | `8001` | listen port (used by `python -m app.main`) |
| `DATABASE_URL` | `sqlite:///./user_service.db` | this service's private DB |
| `LOG_LEVEL` | `INFO` | log verbosity |

## API (`/api/v1`)

| Method | Path | Success | Errors |
|---|---|---|---|
| GET | `/health` | 200 | |
| POST | `/api/v1/users` | 201 | 409 duplicate email, 422 validation |
| GET | `/api/v1/users?limit&offset&status` | 200 | 422 |
| GET | `/api/v1/users/{user_id}` | 200 | 404 |
| PUT | `/api/v1/users/{user_id}` | 200 | 404, 409, 422 |
| POST | `/api/v1/users/{user_id}/activate` | 200 | 404, 409 |
| POST | `/api/v1/users/{user_id}/deactivate` | 200 | 404, 409 |

Error format (all errors, including 404/422/500):

```json
{"error": {"code": "EMAIL_ALREADY_EXISTS", "message": "...", "details": [], "request_id": "..."}}
```

Send `X-Request-ID` to propagate a correlation ID; it is echoed in the response and appears in every JSON log line.

## Data (table `users`)

`id` (UUID str, PK), `name`, `email`, `email_normalized` (UNIQUE), `phone`, `status` (`ACTIVE`|`INACTIVE`), `created_at`, `updated_at`.

## Business rules -> code -> tests

| Rule | Code | Test |
|---|---|---|
| BR-U1 Email unique, case-insensitive (DB UNIQUE constraint decides races) | `service.py` `create/update`, `models.py` | `test_br_u1_*` (incl. 20 concurrent creates -> exactly 1 succeeds) |
| BR-U2 Valid name / email / phone | `schemas.py` | `test_br_u2_*` |
| BR-U3 Status ACTIVE <-> INACTIVE; repeating a transition -> 409 | `service.py` `check_transition` | `test_br_u3_*` |
| BR-U4 INACTIVE users cannot be edited | `service.py` `update` | `test_br_u4_*` |

Booking Service rule (enforced there, using this service): only users with `status == ACTIVE` may book.

## Test

```bash
python -m pytest -v
```

## Structure

```
app/  main.py (app, middleware, error handlers, /health)   routes.py (HTTP only)
      service.py (business rules)   models.py / database.py (data access)
      schemas.py (validation)   errors.py   config.py   logging_config.py
tests/
```

## How other services call it

```
GET http://localhost:8001/api/v1/users/{user_id}   -> 404 if unknown; check "status" == "ACTIVE"; use "email"/"phone" for notifications
```
