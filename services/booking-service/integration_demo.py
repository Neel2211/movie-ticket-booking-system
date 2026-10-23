"""End-to-end smoke test for the movie booking system.

Start all five services first (user 8001, show 8002, booking 8003,
payment 8004, notification 8006) and seed Show Service, then run:

    python integration_demo.py            # uses seat A2 for the success case
    python integration_demo.py A4         # pick another free seat on re-runs

Only needs the 'requests' package.
"""
import sys
import time

import requests

USER = "http://127.0.0.1:8001"
SHOW = "http://127.0.0.1:8002"
BOOKING = "http://127.0.0.1:8003"
PAYMENT = "http://127.0.0.1:8004"
NOTIFY = "http://127.0.0.1:8006"

SEAT_OK = sys.argv[1] if len(sys.argv) > 1 else "A2"
SEAT_FAIL = "A3"
SHOW_ID = 1

failures = 0


def check(label, condition, detail=""):
    global failures
    if not condition:
        failures += 1
    print(f"[{'PASS' if condition else 'FAIL'}] {label} {detail}")


def new_booking(user_id, seat):
    return requests.post(
        f"{BOOKING}/bookings",
        json={"user_id": user_id, "show_id": SHOW_ID, "seat_number": seat},
        timeout=10,
    )


def process(booking_id, payment_success):
    return requests.post(
        f"{BOOKING}/bookings/{booking_id}/process",
        json={"payment_success": payment_success},
        timeout=20,
    )


def main():
    print("== 1. Health checks")
    for name, url in [
        ("user", f"{USER}/health"),
        ("show", f"{SHOW}/health"),
        ("booking", f"{BOOKING}/health"),
        ("payment", f"{PAYMENT}/health"),
        ("notification", f"{NOTIFY}/health"),
    ]:
        try:
            r = requests.get(url, timeout=5)
            check(f"{name}-service healthy", r.status_code == 200)
        except requests.RequestException as exc:
            check(f"{name}-service reachable", False, str(exc))
    if failures:
        print("Start the missing services and run again.")
        sys.exit(1)

    print("\n== 2. Register a user")
    email = f"demo{int(time.time())}@example.com"
    r = requests.post(
        f"{USER}/api/v1/users",
        json={"name": "Demo User", "email": email, "phone": "+919876543210"},
        timeout=10,
    )
    check("user created", r.status_code == 201, r.text[:80])
    user_id = r.json()["id"]

    print("\n== 3. Happy path (seat %s)" % SEAT_OK)
    r = new_booking(user_id, SEAT_OK)
    check("booking created as PENDING", r.status_code == 200 and r.json()["status"] == "PENDING", r.text[:80])
    booking_id = r.json()["booking_id"]
    r = process(booking_id, True)
    check("booking CONFIRMED", r.status_code == 200 and r.json()["final_status"] == "CONFIRMED", r.text[:80])

    print("\n== 4. Double booking is rejected")
    r = new_booking(user_id, SEAT_OK)
    second_id = r.json()["booking_id"]
    r = process(second_id, True)
    check("same seat -> HTTP 409", r.status_code == 409, r.text[:80])
    r = requests.get(f"{BOOKING}/bookings/{second_id}", timeout=10)
    check("losing booking is CANCELLED", r.json()["status"] == "CANCELLED")

    print("\n== 5. Payment failure -> saga compensation (seat %s)" % SEAT_FAIL)
    r = new_booking(user_id, SEAT_FAIL)
    fail_id = r.json()["booking_id"]
    r = process(fail_id, False)
    check("booking CANCELLED after failed payment", r.status_code == 200 and r.json()["final_status"] == "CANCELLED", r.text[:80])
    r = requests.post(f"{SHOW}/seats/reserve", json={"show_id": SHOW_ID, "seat_number": SEAT_FAIL}, timeout=10)
    check("seat was released (can be reserved again)", r.status_code == 200, r.text[:80])
    requests.post(f"{SHOW}/seats/release", json={"show_id": SHOW_ID, "seat_number": SEAT_FAIL}, timeout=10)

    print("\n== 6. User rules")
    r = new_booking("no-such-user", SEAT_FAIL)
    check("unknown user -> HTTP 404", r.status_code == 404, r.text[:80])
    requests.post(f"{USER}/api/v1/users/{user_id}/deactivate", timeout=10)
    r = new_booking(user_id, SEAT_FAIL)
    check("INACTIVE user -> HTTP 409", r.status_code == 409, r.text[:80])

    print("\n== 7. Notifications")
    r = requests.get(f"{NOTIFY}/api/v1/notifications", params={"limit": 500}, timeout=10)
    mine = [n for n in r.json() if n["recipient"] == email]
    check("2 notifications stored for this user", len(mine) == 2, f"(found {len(mine)})")
    for n in mine:
        print("      -", n["subject"], "|", n["message"])

    print("\nRESULT:", "ALL CHECKS PASSED" if not failures else f"{failures} CHECK(S) FAILED")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
