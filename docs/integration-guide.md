# Integration Guide: Payment Service

## Integrations Summary

### 1. Booking Service Integration
* **Trigger**: Initiated when a user completes seat selection and proceeds to payment.
* **Communication**: 
  * Synchronous REST `POST /api/v1/payments` with `Idempotency-Key`.
  * Asynchronous status events published to message broker upon status updates.

### 2. Payment Gateway Integration
* Encapsulates third-party API integration (Stripe / Razorpay / Mock Gateway).
* Features automated timeout handling, network retry limits, and webhook signature verification for async status callbacks.