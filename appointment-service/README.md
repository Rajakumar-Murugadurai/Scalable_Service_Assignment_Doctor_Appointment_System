# Appointment Service

Part of the **Telehealth Microservices** application (SEZG583 – Scalable Services).

Books patient appointments. Collaborates with the **Doctor Service** over REST to
validate a slot and reserve it before confirming an appointment.

## Tech Stack
- Python 3.11 + FastAPI
- PostgreSQL (own database)
- SQLAlchemy ORM
- httpx (synchronous REST client for inter-service calls)
- Docker + Kubernetes

## API Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/appointments` | Book an appointment (calls Doctor Service) |
| GET | `/appointments` | List appointments |
| GET | `/appointments/{id}` | Get an appointment |
| DELETE | `/appointments/{id}` | Cancel an appointment (releases slot) |

## Inter-service communication
Set via the `DOCTOR_SERVICE_URL` environment variable:
- Local / docker-compose: `http://doctor-service:8000`
- Kubernetes: `http://doctor-service:8000` (K8s Service DNS)

## Run locally (without Docker)
```powershell
cd appointment-service
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DOCTOR_SERVICE_URL="http://localhost:8001"
uvicorn app.main:app --reload --port 8002
```
Open http://localhost:8002/docs for interactive Swagger UI.

## Build Docker image
```powershell
docker build -t appointment-service:1.0 .
```

## Deploy to Kubernetes
```powershell
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/deployment.yaml
```

