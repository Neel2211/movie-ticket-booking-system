# Movie Ticket Booking System

## Overview

This project implements a distributed Movie Ticket Booking System using a microservices architecture. The system was developed as part of the Scalable Services course and demonstrates service decomposition, inter-service communication, concurrency control, idempotency, saga orchestration, containerization, Docker Compose deployment, and Kubernetes deployment.

### Services

- User Service
- Show Service
- Booking Service
- Payment Service
- Notification Service

### Key Features

- Microservices architecture
- Database-per-Service pattern
- REST API communication
- Concurrency control for seat booking
- Idempotent payment processing
- Saga orchestration and compensation
- Docker containerization
- Docker Compose deployment
- Kubernetes deployment using Minikube
- Kubernetes self-healing demonstration

---

# System Architecture

The application consists of five independently deployable services:

| Service | Responsibility | Port |
|----------|----------|----------|
| User Service | User management and validation | 8001 |
| Show Service | Shows and seat inventory management | 8002 |
| Booking Service | Booking workflow and saga orchestration | 8003 |
| Payment Service | Payment processing and idempotency | 8004 |
| Notification Service | User notifications | 8006 |

---

# Prerequisites

## Docker Deployment

Install:

- Docker Desktop
- Docker Compose

Verify:

```powershell
docker --version
docker compose version
```

## Kubernetes Deployment (Advanced Task)

Install:

- Docker Desktop
- kubectl
- Minikube

Verify:

```powershell
kubectl version --client
minikube version
```

---

# Docker Compose Deployment

## Build and Start All Services

```powershell
docker compose up --build
```

## Verify Running Containers

```powershell
docker ps
```

Expected containers:

```text
user-service
show-service
booking-service
payment-service
notification-service
```

## Stop Deployment

```powershell
docker compose down
```

---

# Service Endpoints

| Service | URL |
|----------|----------|
| User Service | http://localhost:8001/docs |
| Show Service | http://localhost:8002/docs |
| Booking Service | http://localhost:8003/docs |
| Payment Service | http://localhost:8004/docs |
| Notification Service | http://localhost:8006/docs |

---

# Integration Validation

Navigate to:

```powershell
cd services\booking-service
```

Activate virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

Run integration validation:

```powershell
python integration_demo.py
```

Expected result:

```text
RESULT: ALL CHECKS PASSED
```

The integration test validates:

- Service health checks
- User registration
- Successful booking workflow
- Double-booking prevention
- Payment failure compensation
- User validation rules
- Notification generation

---

# Assignment 1 Features

## Concurrency Control

The system prevents multiple users from booking the same seat simultaneously.

Validation script:

```powershell
python concurrency_test.py
```

Expected behavior:

```text
1 successful reservation
Remaining reservations rejected
```

## Idempotent Payments

Duplicate payment requests are detected using idempotency keys.

## Saga Pattern

Booking Service acts as the Saga Orchestrator.

### Success Flow

```text
PENDING
→ RESERVED
→ CONFIRMED
```

### Compensation Flow

```text
PENDING
→ RESERVED
→ PAYMENT_FAILED
→ CANCELLED
```

---

# Docker Containerization

Each microservice contains:

```text
Dockerfile
.dockerignore
```

Images can be built individually:

```powershell
docker build -t user-service services/user-service
docker build -t show-service services/show-services
docker build -t booking-service services/booking-service
docker build -t payment-service services/payment-service
docker build -t notification-service services/notification-service
```

---

# Kubernetes Deployment

Kubernetes manifests are available in:

```text
k8s/
```

## Deploy All Services

```powershell
kubectl apply -f k8s/
```

## Verify Pods

```powershell
kubectl get pods
```

Expected:

```text
user-service
show-service
booking-service
payment-service
notification-service
```

in Running state.

## Verify Services

```powershell
kubectl get svc
```

---

# Access Kubernetes Deployment

Example:

```powershell
kubectl port-forward service/booking-service 9003:8003
```

Open:

```text
http://localhost:9003/docs
```

---

# Kubernetes Self-Healing Demonstration

Delete a running pod:

```powershell
kubectl delete pod <pod-name>
```

Example:

```powershell
kubectl delete pod booking-service-xxxxx
```

Kubernetes automatically recreates the pod.

Verify:

```powershell
kubectl get pods
```

A new pod instance should appear in Running state.

---

# Deployment Troubleshooting Scenario

## Problem

Booking Service container failed to start after Docker Compose deployment.

### Symptom

```text
exec: "uvicorn": executable file not found in $PATH
```

## Root Cause

Booking Service dependency configuration contained:

```text
unicorn==2.1.4
```

instead of:

```text
uvicorn
```

## Solution

Updated requirements:

```text
uvicorn[standard]>=0.30
```

Rebuilt image:

```powershell
docker compose build booking-service
```

## Validation

```powershell
docker compose up --build
```

and

```text
RESULT: ALL CHECKS PASSED
```

confirmed successful deployment.

---

# Repository Structure

```text
movie-ticket-booking-system
│
├── docker-compose.yml
├── README.md
├── k8s
│   ├── user-service.yaml
│   ├── show-service.yaml
│   ├── booking-service.yaml
│   ├── payment-service.yaml
│   └── notification-service.yaml
│
└── services
    ├── user-service
    ├── show-services
    ├── booking-service
    ├── payment-service
    └── notification-service
```

---

# Authors

Group 9

- Neel Gujar
- Yamuna P Hegade
- Bhandari Akshay Sunil
- Naveen Venkat P

---

# License

Academic project developed for the Scalable Services course.