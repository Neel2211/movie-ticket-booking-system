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

Port: 8005

Required APIs

POST /notifications