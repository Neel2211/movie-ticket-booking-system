# Service Contracts
 
## User Service
 
### Create User
POST /users
 
Request:
{
  "name": "Neel",
  "email": "neel@example.com"
}
 
Response:
{
  "user_id": 1,
  "name": "Neel",
  "email": "neel@example.com"
}
 
### Get User
GET /users/{user_id}
 
---
 
## Show Service
 
### Get Shows
GET /shows
 
### Reserve Seat
POST /seats/reserve
 
Request:
{
  "show_id": 1,
  "seat_number": "A1"
}
 
Response:
{
  "success": true
}
 
### Release Seat
POST /seats/release
 
Request:
{
  "show_id": 1,
  "seat_number": "A1"
}
 
---
 
## Booking Service
 
### Create Booking
POST /bookings
 
Request:
{
  "user_id": 1,
  "show_id": 1,
  "seat_number": "A1"
}
 
Response:
{
  "booking_id": 101,
  "status": "PENDING"
}
 
### Get Booking
GET /bookings/{booking_id}
 
---
 
## Payment Service
 
### Process Payment
POST /payments
 
Request:
{
  "booking_id": 101,
  "amount": 200,
  "idempotency_key": "ABC123"
}
 
Response:
{
  "payment_id": 5001,
  "status": "SUCCESS"
}
 
---
 
## Notification Service
 
### Send Notification
POST /notifications
 
Request:
{
  "booking_id": 101,
  "message": "Booking Confirmed"
}
 