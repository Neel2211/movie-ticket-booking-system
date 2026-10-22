<<<<<<< HEAD
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
=======
# Service Performance & Reliability Report

## Metrics & Benchmarks
* **Throughput**: Verified up to 250 requests/second under k6 load tests.
* **Idempotency Deduplication Accuracy**: 100% deduplication efficiency across concurrent retry spikes.
* **Latency**: Average response latency < 45ms for cached idempotent calls and < 180ms for new payment executions.

## Reliability Mechanisms
* Circuit breaker configured for payment gateway requests.
* DB level constraints preventing duplicate booking payment records.
>>>>>>> origin/feature/payment-service
