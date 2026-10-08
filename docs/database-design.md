# Database Design
 
## User Service Database (user.db)
 
Table: users
 
- user_id (PK)
- name
- email
 
---
 
## Show Service Database (show.db)
 
Table: shows
 
- show_id (PK)
- movie_name
- show_time
 
Table: seats
 
- seat_id (PK)
- show_id
- seat_number
- status
 
Status Values:
- AVAILABLE
- RESERVED
- BOOKED
 
---
 
## Booking Service Database (booking.db)
 
Table: bookings
 
- booking_id (PK)
- user_id
- show_id
- seat_number
- status
- created_at
 
Status Values:
- PENDING
- RESERVED
- CONFIRMED
- PAYMENT_FAILED
- CANCELLED
 
---
 
## Payment Service Database (payment.db)
 
Table: payments
 
- payment_id (PK)
- booking_id
- amount
- idempotency_key
- status
- created_at
 
Status Values:
- SUCCESS
- FAILED
 
Important:
idempotency_key must be unique
 
---
 
## Notification Service Database (notification.db)
 
Table: notifications
 
- notification_id (PK)
- booking_id
- message
- sent_at
 