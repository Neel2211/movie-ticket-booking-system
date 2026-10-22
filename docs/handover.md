<<<<<<< HEAD
# Handover

Booking Service completed.

Implemented:

- Create booking
- Get booking
- Update status
- State transitions
- Mock Saga
- Concurrency challenge
- Idempotency challenge

Pending:

- User Service integration
- Show Service integration
- Payment Service integration
- Notification Service integration

Team Responsibilities:

Yamuna
- User Service

Akshay
- Show Service

Naveen
- Payment Service

Ports:

8001 User Service
8002 Show Service
8003 Booking Service
8004 Payment Service
8006 Notification Service
=======
# Handover Documentation - Notification Service

## Overview
The Notification Service handles multi-channel alerts (Email, SMS, Push) for the Movie Ticket Booking System. It runs on port **8006** under base path `/api/v1/notifications`.

## Running Locally & Testing
1. Start the service:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8006 --reload
>>>>>>> origin/feature/notification-service
