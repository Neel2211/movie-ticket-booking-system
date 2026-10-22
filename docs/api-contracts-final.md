<<<<<<< HEAD
# API Contracts

## User Service (Port 8001)

POST /users

GET /users/{id}

## Show Service (Port 8002)

GET /shows

POST /seats/reserve

Request:
{
  "show_id": 1,
  "seat_number": "A1"
}

POST /seats/release

Request:
{
  "show_id": 1,
  "seat_number": "A1"
}

## Booking Service (Port 8003)

POST /bookings

GET /bookings/{id}

PUT /bookings/{id}/status

POST /bookings/{id}/process

## Payment Service (Port 8004)

POST /payments

Request:
{
  "idempotency_key": "PAY123"
}

## Notification Service (Port 8006)

POST /notifications
=======
# API Contracts - Notification Service (v1)

Base URL: `http://localhost:8006/api/v1`

## 1. Send Notification
- **Endpoint**: `POST /notifications`
- **Headers**: 
  - `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "recipient": "user@example.com",
    "channel": "EMAIL",
    "template_id": "booking_confirmation",
    "payload": {
      "booking_id": 103,
      "movie_title": "Inception",
      "showtime": "2026-10-25T18:30:00",
      "seats": ["A1", "A2"]
    }
  }
>>>>>>> origin/feature/notification-service
