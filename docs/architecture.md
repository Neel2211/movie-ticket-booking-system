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