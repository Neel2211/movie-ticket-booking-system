<<<<<<< HEAD
# Integration Guide

## User Service

Port: 8001

Required APIs

POST /users

GET /users/{id}

---

## Show Service

Port: 8002

Required APIs

POST /seats/reserve

POST /seats/release

GET /shows

---

## Booking Service

Port: 8003

Implemented by Neel

---

## Payment Service

Port: 8004

Required APIs

POST /payments

Supports idempotency_key

---

## Notification Service

Port: 8006

Required APIs

POST /notifications
=======
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
>>>>>>> origin/feature/payment-service
