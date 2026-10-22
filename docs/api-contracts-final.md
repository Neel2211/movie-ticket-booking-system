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