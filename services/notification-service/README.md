# Notification Service - Movie Ticket Booking System

The **Notification Service** is a core microservice responsible for dispatching multi-channel alerts (Email, SMS) for booking confirmations, reminders, and system updates within the Movie Ticket Booking System.

---

## 🚀 Tech Stack
* **Framework**: FastAPI (Python 3.11+)
* **Database**: SQLite (Configured with WAL mode and `timeout=30` to handle concurrent queue updates)
* **ORM**: SQLAlchemy
* **Testing**: Pytest

---

## 📌 Service Specifications
* **Base URL**: `/api/v1/notifications`
* **Port**: `8006`
* **Interactive Docs**: `http://localhost:8006/docs` (Swagger UI)

---

## 🛠️ Core Features & Design
1. **Multi-Channel Dispatch**: Supports sending structured messages across channels like `EMAIL` and `SMS`.
2. **Delivery Status Tracking**: Logs and exposes delivery status endpoints (`SENT`, `PENDING`, `FAILED`) for auditing.
3. **Resilient Logging**: Tracks provider message IDs and transaction metadata for downstream coordination.

---

## ⚙️ Running Locally

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt

2. **Run tests**:
   ```bash
   python -m pytest -v