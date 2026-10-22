# Handover Documentation - Notification Service

## Overview
The Notification Service handles multi-channel alerts (Email, SMS, Push) for the Movie Ticket Booking System. It runs on port **8006** under base path `/api/v1/notifications`.

## Running Locally & Testing
1. Start the service:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8006 --reload