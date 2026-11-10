# Doctor Service

Part of the **Telehealth Microservices** application (SEZG583 – Scalable Services).

Manages doctors and their availability slots. Exposes a REST API consumed by the
Appointment Service.

## Tech Stack
- Python 3.11 + FastAPI
- PostgreSQL (own database — database-per-service pattern)
- SQLAlchemy ORM
- Docker + Kubernetes

## API Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/doctors` | Create a doctor |
| GET | `/doctors` | List doctors |
| GET | `/doctors/{id}` | Get a doctor |
| POST | `/doctors/{id}/availability` | Add an availability slot |
| GET | `/doctors/{id}/availability` | List a doctor's slots |
| GET | `/availability/{slot_id}` | Get a slot (used by Appointment Service) |
| PATCH | `/availability/{slot_id}/book` | Reserve a slot |
| PATCH | `/availability/{slot_id}/release` | Free a slot |

## Run locally (without Docker)
```powershell
cd doctor-service
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Requires a local Postgres; or just use docker-compose from repo root.
uvicorn app.main:app --reload --port 8001
```
Open http://localhost:8001/docs for interactive Swagger UI.

## Build Docker image
```powershell
docker build -t doctor-service:1.0 .
```

## Deploy to Kubernetes
```powershell
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/deployment.yaml
```

