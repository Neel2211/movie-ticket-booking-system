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