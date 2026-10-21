# Show Service

Owns movie show information and seat availability.

## Technology

- Python 3.14
- FastAPI
- SQLite
- SQLAlchemy
- pytest

## Port

8002

## API endpoints

| Method | Route | Purpose |
|---|---|---|
| GET | /shows | List shows |
| POST | /seats/reserve | Reserve an available seat |
| POST | /seats/release | Release a reserved seat |
| GET | /health | Health check |

Swagger UI: http://localhost:8002/docs

## Database

The service owns its own SQLite database: show.db.

Tables:
- shows
- seats

No other service may access this database directly.

## Configuration

- SHOW_PORT
- SHOW_DATABASE_URL
- LOG_LEVEL

See .env.example for example values.

## Install dependencies

    python -m pip install -r requirements.txt

## Seed sample data

Run from this directory:

    python -m app.seed_data

## Start the service

    python -m app.main

## Run tests

    python -m pytest -v

## Concurrency guarantee

Reservation uses a conditional database update that succeeds
only when the seat is AVAILABLE. The concurrency test sends
20 simultaneous requests for the same seat and checks that
exactly one succeeds.

## Business rules

- BR-S1: Only an AVAILABLE seat can be reserved.
- BR-S2: The requested seat must exist for the specified show.
- BR-S3: Only a RESERVED seat can be released.
- BR-S4: Concurrent reservations must not over-allocate a seat.