# CricBuzz Live Match Tracker

## Project Overview

This project is a backend system for live cricket scoring similar to CricBuzz.

It supports:
- Match creation
- Player management
- Ball-by-ball scoring
- Live scorecards
- Batsman statistics
- Bowler figures
- Cricket validations
- Docker deployment
- Kubernetes deployment

---

# Tech Stack

- FastAPI
- Python
- SQLAlchemy
- SQLite / PostgreSQL
- Docker
- Kubernetes
- Rancher Desktop

---

# Features

## Match APIs
- Create Match
- Add Players
- Record Delivery

## Analytics APIs
- Live Scorecard
- Batsman Scorecard
- Bowler Figures

## Cricket Rules Implemented
- No duplicate ball entries
- 6 legal deliveries per over
- Wides and no-balls don't count as legal deliveries
- Innings ending logic
- Bowler over limit validation

---

# Run Locally

## Create Virtual Environment

```bash
python3 -m venv venv
```

## Activate Virtual Environment

```bash
source venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run FastAPI Server

```bash
uvicorn main:app --reload
```

---

# Docker Commands

## Build Docker Image

```bash
docker build -t cricbuzz-api .
```

## Run Docker Container

```bash
docker run -p 8000:8000 cricbuzz-api
```

---

# Kubernetes Commands

## Apply Deployment

```bash
kubectl apply -f k8s/api-deployment.yml
```

## Apply Service

```bash
kubectl apply -f k8s/api-service.yml
```

## Check Pods

```bash
kubectl get pods
```

---

# API Endpoints

| Method | Endpoint |
|---|---|
| POST | /match |
| POST | /player |
| POST | /delivery |
| GET | /scorecard/{match_id} |
| GET | /batsman/{name} |
| GET | /bowler/{name} |

---

# Kubernetes Features

- Deployment
- Service
- ConfigMap
- Secret
- Liveness Probe
- Readiness Probe
- 2 API Replicas

---

# Author

Vamsi Gulla