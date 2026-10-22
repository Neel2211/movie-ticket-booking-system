# Architecture & Design Patterns: Payment Service

## Service Overview
The **Payment Service** is a dedicated microservice in the Movie Ticket Booking System responsible for processing transactions, maintaining payment records, enforcing idempotency, and coordinating with third-party payment gateways[cite: 6].

## Key Design Patterns
1. **Database-per-Service**: Maintains a separate database (`payment.sqlite`) ensuring high data isolation and microservice autonomy[cite: 6].
2. **Idempotency Key Pattern**: Intercepts inbound requests via an `Idempotency-Key` header to safely handle retries and prevent double charges[cite: 6].
3. **Gateway Abstraction Layer**: Wraps external payment providers behind a unified interface, allowing easy swapping between simulated gateways and real providers[cite: 6].
4. **Saga Orchestration Integration**: Participates in distributed transactions by emitting state updates and executing compensating operations (refunds) on failure[cite: 6].