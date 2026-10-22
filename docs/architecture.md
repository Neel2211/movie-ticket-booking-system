# Architecture & Design Patterns - Notification Service

## Tech Stack
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy
- **Database**: SQLite (Configured with WAL mode and `timeout=30` to handle concurrent queue updates)
- **Messaging/Integration**: Event-driven or direct REST triggers from Booking and Payment microservices.

## Core Design Considerations
1. **Asynchronous Dispatch**: Ensures that slow third-party SMS/Email gateway responses do not block core booking transactions.
2. **Retry & Fallback Mechanism**: Handles transient network failures when connecting to external notification providers (e.g., SMTP, Twilio, SendGrid).
3. **Idempotency/Deduplication**: Prevents sending duplicate notifications for the same booking event if retry loops overlap.