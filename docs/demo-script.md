<<<<<<< HEAD
# Demo Script

## Challenge 1 - Concurrency

Run:

python concurrency_test.py

Expected:

Successful Reservations: 1
Failed Reservations: 19

---

## Challenge 2 - Idempotency

Endpoint:

POST /payments

Request:

{
  "idempotency_key": "PAY123"
}

First request:

Payment processed

Subsequent requests:

Duplicate request

---

## Challenge 3C - Saga

Create booking

POST /bookings

Process booking

POST /bookings/{id}/process

Request:

{
  "payment_success": true
}

Expected:

CONFIRMED

Request:

{
  "payment_success": false
}

Expected:

CANCELLED
=======
# Demonstration Walk-Through Script

## 1. Service Health Check (1 min)
Verify that the service container is active and accepting traffic:
```bash
curl http://localhost:8004/health
>>>>>>> origin/feature/payment-service
