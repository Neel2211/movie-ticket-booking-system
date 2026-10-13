# Run Booking Service

## Clone Repository

```bash
git clone https://github.com/Neel2211/movie-ticket-booking-system.git
```

## Checkout Branch

```bash
git checkout feature/booking-service
```

## Navigate

```bash
cd services/booking-service
```

## Create Virtual Environment

```bash
python -m venv venv
```

## Activate Virtual Environment

Git Bash:

```bash
source venv/Scripts/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run Service

```bash
python -m uvicorn app.main:app --reload --port 8003
```

## Swagger

```text
http://127.0.0.1:8003/docs
```

## Health Check

```text
http://127.0.0.1:8003/health
```