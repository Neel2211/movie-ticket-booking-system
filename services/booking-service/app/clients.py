"""HTTP clients used by Booking Service to talk to the other services.

Booking Service is the orchestrator: it never touches another service's
database, it only calls their REST APIs.
"""
import requests

USER_SERVICE_URL = "http://127.0.0.1:8001"
SHOW_SERVICE_URL = "http://127.0.0.1:8002"
PAYMENT_SERVICE_URL = "http://127.0.0.1:8004"
NOTIFICATION_SERVICE_URL = "http://127.0.0.1:8006"

TIMEOUT_SECONDS = 5
TICKET_PRICE = 250.0


def fetch_user(user_id):
    """GET a user from User Service.

    Returns the user dict, or None when the user does not exist.
    Raises requests.RequestException if the service is unreachable or fails.
    """
    response = requests.get(
        f"{USER_SERVICE_URL}/api/v1/users/{user_id}",
        timeout=TIMEOUT_SECONDS
    )
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()


def reserve_seat_remote(show_id, seat_number):
    """Ask Show Service to reserve a seat. Returns the HTTP status code.

    200 = reserved, 404 = seat not found, 409 = seat not available.
    Raises requests.RequestException if the service is unreachable.
    """
    response = requests.post(
        f"{SHOW_SERVICE_URL}/seats/reserve",
        json={"show_id": show_id, "seat_number": seat_number},
        timeout=TIMEOUT_SECONDS
    )
    return response.status_code


def release_seat_remote(show_id, seat_number):
    """Ask Show Service to release a seat (saga compensation).

    Best effort: returns the HTTP status code, or None if unreachable.
    """
    try:
        response = requests.post(
            f"{SHOW_SERVICE_URL}/seats/release",
            json={"show_id": show_id, "seat_number": seat_number},
            timeout=TIMEOUT_SECONDS
        )
        return response.status_code
    except requests.RequestException:
        return None


def charge_payment(booking_id, idempotency_key, amount, currency="INR"):
    """Charge through Payment Service. Returns True only on SUCCESS."""
    try:
        response = requests.post(
            f"{PAYMENT_SERVICE_URL}/api/v1/payments",
            json={
                "booking_id": booking_id,
                "amount": amount,
                "currency": currency
            },
            headers={"Idempotency-Key": idempotency_key},
            timeout=TIMEOUT_SECONDS
        )
        if response.status_code not in (200, 201):
            return False
        return response.json().get("status") == "SUCCESS"
    except (requests.RequestException, ValueError):
        return False


def send_notification(recipient, subject, message):
    """Send an e-mail notification. Best effort, never raises."""
    try:
        requests.post(
            f"{NOTIFICATION_SERVICE_URL}/api/v1/notifications",
            json={
                "recipient": recipient,
                "channel": "EMAIL",
                "subject": subject,
                "message": message
            },
            timeout=TIMEOUT_SECONDS
        )
    except requests.RequestException:
        pass
