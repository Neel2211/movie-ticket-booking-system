import threading
import requests

success = 0
failure = 0


def reserve():
    global success, failure

    try:
        response = requests.post(
            "http://127.0.0.1:8003/reserve-seat",
            params={
                "show_id": 1,
                "seat_number": "A1"
            }
        )

        if response.status_code == 200:
            success += 1
        else:
            failure += 1

    except Exception:
        failure += 1


threads = []

for _ in range(20):
    t = threading.Thread(target=reserve)
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print("Successful Reservations:", success)
print("Failed Reservations:", failure)