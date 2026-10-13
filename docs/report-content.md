# Problem Statement

The objective is to design and implement a microservices-based movie ticket booking system demonstrating distributed systems concepts such as concurrency control, idempotency, and Saga orchestration.

# Booking Service

The Booking Service acts as the Saga orchestrator and manages booking lifecycle states.

# Concurrency Challenge

The system prevents multiple users from reserving the same seat simultaneously.

# Idempotency Challenge

Duplicate payment requests with the same idempotency key are safely handled.

# Saga Challenge

Successful payments confirm bookings, while failed payments trigger compensation actions and booking cancellation.
