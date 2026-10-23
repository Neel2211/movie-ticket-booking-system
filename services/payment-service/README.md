# Payment Service - Movie Ticket Booking System

The **Payment Service** is a core microservice responsible for handling secure financial transactions, idempotency enforcement, race condition mitigation, and distributed transaction rollbacks (SAGA compensation) for the Movie Ticket Booking System.

---

## 🚀 Tech Stack
* **Framework**: FastAPI (Python 3.11+)
* **Database**: SQLite (Configured with WAL mode and `timeout=30` to handle write concurrency contention)
* **ORM**: SQLAlchemy
* **Testing**: Pytest

---

## 📌 Service Specifications
* **Base URL**: `/api/v1/payments`
* **Port**: `8004`
* **Interactive Docs**: `http://localhost:8004/docs` (Swagger UI)

---

## 🛠️ Core Features & Design Patterns Addressed

1. **Concurrency Control**: 
   - Uses SQLite Write-Ahead Logging (WAL) and connection timeout configurations (`timeout=30`) to prevent file-locking conflicts during parallel thread testing.
2. **Idempotency Protection**: 
   - Enforces unique `Idempotency-Key` headers on payment creation requests. Duplicate calls return cached responses to prevent double-charging users.
3. **SAGA Compensation (Distributed Rollbacks)**: 
   - Exposes a dedicated refund endpoint (`POST /api/v1/payments/{payment_id}/refund`) to automatically revert completed payments if downstream booking or seat reservation steps fail.

---

## ⚙️ Running Locally

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt

2. **Run tests**:
   ```bash
   python -m pytest -v
