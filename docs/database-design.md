<<<<<<< HEAD
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
 
=======
# Database Design: Payment Service

## Overview
The Payment Service operates on an isolated SQLite storage layer (`payment.sqlite`) following the database-per-service pattern.

## Tables

### 1. `payments`
Stores primary transaction details and payment lifecycle state.
* `id` (INTEGER, Primary Key, Auto-increment)
* `booking_id` (INTEGER, Unique, Not Null)
* `amount` (REAL, Not Null)
* `currency` (TEXT, Default: 'INR')
* `status` (TEXT, Not Null) — Enum: `PENDING`, `SUCCESS`, `FAILED`, `REFUNDED`
* `gateway_transaction_id` (TEXT, Nullable)
* `created_at` (TIMESTAMP, Default: CURRENT_TIMESTAMP)
* `updated_at` (TIMESTAMP, Default: CURRENT_TIMESTAMP)

### 2. `idempotency_logs`
Tracks processed idempotent request keys to prevent duplicate transaction charges.
* `idempotency_key` (TEXT, Primary Key)
* `response_payload` (TEXT, Not Null) — Serialized JSON response
* `status_code` (INTEGER, Not Null)
* `created_at` (TIMESTAMP, Default: CURRENT_TIMESTAMP)

### 3. `refunds`
Logs compensating transactions and refund triggers.
* `id` (INTEGER, Primary Key, Auto-increment)
* `payment_id` (INTEGER, Foreign Key -> `payments.id`)
* `amount` (REAL, Not Null)
* `reason` (TEXT, Not Null)
* `status` (TEXT, Not Null) — Enum: `PENDING`, `COMPLETED`, `FAILED`
* `created_at` (TIMESTAMP, Default: CURRENT_TIMESTAMP)
>>>>>>> origin/feature/payment-service
