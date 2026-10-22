import concurrent.futures
import time
import requests
import random

URL = "http://localhost:8004/api/v1/payments"
IDEMPOTENCY_KEY = f"concurrency-key-{int(time.time())}"
BOOKING_ID = int(time.time()) % 10000 + 500

def send_payment_request(request_num):
    headers = {
        "Content-Type": "application/json",
        "Idempotency-Key": IDEMPOTENCY_KEY
    }
    payload = {
        "booking_id": BOOKING_ID,
        "amount": 500.00,
        "currency": "INR"
    }
    time.sleep(random.uniform(0.01, 0.05))
    start_time = time.time()
    try:
        response = requests.post(URL, json=payload, headers=headers, timeout=5)
        elapsed = round((time.time() - start_time) * 1000, 2)
        
        # Safely parse JSON or fallback to text if empty/error page
        try:
            body = response.json()
        except Exception:
            body = {"raw_text": response.text}

        return {
            "req_num": request_num,
            "status_code": response.status_code,
            "elapsed_ms": elapsed,
            "body": body
        }
    except Exception as e:
        return {
            "req_num": request_num,
            "status_code": "ERROR",
            "elapsed_ms": 0,
            "error": str(e)
        }

def run_concurrency_test(total_requests=5):
    print("=" * 65)
    print(f"🔥 STARTING CONCURRENCY TEST ({total_requests} PARALLEL THREADS)")
    print(f"📍 Target Endpoint : {URL}")
    print(f"🔑 Idempotency Key  : {IDEMPOTENCY_KEY}")
    print(f"🎟️  Booking ID      : {BOOKING_ID}")
    print("=" * 65 + "\n")

    with concurrent.futures.ThreadPoolExecutor(max_workers=total_requests) as executor:
        futures = [executor.submit(send_payment_request, i + 1) for i in range(total_requests)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    results.sort(key=lambda x: x["req_num"])

    print(f"{'Req #':<8} | {'Status':<10} | {'Latency (ms)':<14} | {'Details'}")
    print("-" * 65)

    for res in results:
        status = res["status_code"]
        latency = f"{res['elapsed_ms']} ms"
        body = res.get("body", {})
        
        if status in (200, 201):
            details = f"Payment ID: {body.get('id')} | Txn: {body.get('gateway_transaction_id')}"
        elif status == 409:
            details = "Conflict / Handled Idempotency"
        else:
            details = f"Response: {body.get('raw_text', body)}"

        print(f"Req #{res['req_num']:<4} | {status:<10} | {latency:<14} | {details}")

    print("\n" + "=" * 65)

if __name__ == "__main__":
    run_concurrency_test(total_requests=5)