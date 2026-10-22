# Handover Documentation

## System Overview
* **Service Name**: Payment Service
* **Primary Responsibilities**: Payment processing, idempotency protection, payment status tracking, and compensation handling.
* **Tech Stack**: Python 3.14, FastAPI, SQLite / SQLAlchemy, Pydantic.

## Key Configuration Variables
Stored in `.env`:
* `PORT`: `8004`
* `DATABASE_URL`: `sqlite:///./payment.sqlite`
* `GATEWAY_API_KEY`: Secrets/API keys for external payment provider.
* `ENVIRONMENT`: `development` / `production`

## Operational Contacts
* **Primary Team**: Payment Core Engineering
* **Alert Channel**: `#payment-service-alerts`