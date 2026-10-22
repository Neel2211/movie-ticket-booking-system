# Final API Specifications: Payment Service

## Base URL
`http://localhost:8004/api/v1/payments`

## Endpoints

### 1. Process Payment
* **URL**: `/`
* **Method**: `POST`
* **Headers**:
  * `Content-Type: application/json`
  * `Idempotency-Key: <uuid-string>` (Mandatory)

#### Request Body
```json
{
  "booking_id": 101,
  "amount": 450.00,
  "currency": "INR"
}