<<<<<<< HEAD
<<<<<<< HEAD
# Movie Ticket Booking System
 
## Team
 
- Neel - Booking Service + Integration
- Yamuna - User Service
- Akshay - Show Service
- Naveen - Payment Service
- Notification Service - Shared
 
## Technology Stack
 
- Python 3.14
- FastAPI
- SQLite
- REST APIs
- pytest
- Swagger/OpenAPI
 
## Services
 
1. User Service
2. Show Service
3. Booking Service
4. Payment Service
5. Notification Service
 
## Contended Resource
 
Seats
 
## Cross-Service Transaction
 
Book Seat → Reserve Seat → Payment → Confirmation → Notification
 
## Unsafe Operation
 
Payment
 
## Mock Failing Dependency
 
Payment Gateway
 
## Concurrency Challenge
 
20 users booking same seat
 
## Idempotency Challenge
 
Multiple payment requests with same idempotency key
 
## Saga Challenge
 
Payment failure triggers seat release
 
## Business Rules
 
1. A seat can only be reserved once.
2. A seat must be available before reservation.
3. Payment can only be performed for a reserved booking.
4. Booking becomes confirmed only after successful payment.
5. Failed payment releases the reserved seat.
=======
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
>>>>>>> origin/feature/notification-service
=======
# Architecture & Design Patterns: Payment Service

## Service Overview
The **Payment Service** is a dedicated microservice in the Movie Ticket Booking System responsible for processing transactions, maintaining payment records, enforcing idempotency, and coordinating with third-party payment gateways[cite: 6].

## Key Design Patterns
1. **Database-per-Service**: Maintains a separate database (`payment.sqlite`) ensuring high data isolation and microservice autonomy[cite: 6].
2. **Idempotency Key Pattern**: Intercepts inbound requests via an `Idempotency-Key` header to safely handle retries and prevent double charges[cite: 6].
3. **Gateway Abstraction Layer**: Wraps external payment providers behind a unified interface, allowing easy swapping between simulated gateways and real providers[cite: 6].
4. **Saga Orchestration Integration**: Participates in distributed transactions by emitting state updates and executing compensating operations (refunds) on failure[cite: 6].
>>>>>>> origin/feature/payment-service
