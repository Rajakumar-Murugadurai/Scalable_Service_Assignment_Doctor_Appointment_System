# Telehealth Microservices — SEZG583 Scalable Services Assignment

> Microservices Development & Deployment — Healthcare / Telehealth domain.
> Two implemented services: **Doctor Service** and **Appointment Service**.

---

## 1. Member Details
| Name | Student ID | Email |
|------|-----------|-------|
| _<your name>_ | _<your ID>_ | _<your email>_ |

---

## 2. Application Description
A **Telehealth / Online Doctor Appointment** platform that lets patients find
doctors, view their available time slots, and book virtual consultations. The
system is decomposed into independent microservices, each owning its data and
deployable separately.

---

## 3. Design & Architecture (Part 1)

### 3.1 System Operations
**Commands**
- `createOrder` → `bookAppointment`
- `cancelAppointment`
- `addDoctor`
- `addAvailability`

**Queries**
- `listDoctors`
- `getDoctorAvailability`
- `getAppointmentStatus`

### 3.2 Business Capabilities → Services
| Business Capability | Microservice | Status |
|---------------------|--------------|--------|
| Doctor & Availability Management | **Doctor Service** | ✅ Implemented |
| Appointment Management | **Appointment Service** | ✅ Implemented |
| Patient Management | Patient Service | Design only |
| Payments | Payment Service | Design only |
| Notifications | Notification Service | Design only |

### 3.3 Operation → Service Assignment & Collaboration
- **Doctor Service**: `addDoctor`, `addAvailability`, `listDoctors`,
  `getDoctorAvailability`, reserve/release slot.
- **Appointment Service**: `bookAppointment`, `cancelAppointment`,
  `getAppointmentStatus`.
- **Collaboration**: `bookAppointment` → Appointment Service calls Doctor
  Service over REST to (1) validate the slot and (2) mark it booked. On cancel
  it releases the slot.

### 3.4 Architecture Diagram
```
                     ┌──────────────┐
      Patient ─────▶ │  Client/Postman │
                     └───────┬────────┘
             ┌───────────────┴───────────────┐
             ▼                               ▼
   ┌─────────────────────┐        ┌──────────────────────┐
   │ Appointment Service │──REST─▶│   Doctor Service     │
   │  (FastAPI)          │        │   (FastAPI)          │
   │        │            │        │         │            │
   │        ▼            │        │         ▼            │
   │ appointment-postgres│        │   doctor-postgres    │
   └─────────────────────┘        └──────────────────────┘
          (own DB)                       (own DB)

   All running as Pods inside a Minikube Kubernetes cluster.
```

---

## 4. Implementation (Part 2)

### Technologies
| Concern | Choice |
|---------|--------|
| Language / framework | Python 3.11 + FastAPI |
| Database | PostgreSQL (database-per-service) |
| ORM | SQLAlchemy |
| Inter-service comms | REST over HTTP (httpx) |
| Containers | Docker |
| Orchestration | Kubernetes (Minikube) |
| API testing | Postman |

### Project Structure
```
SS_Assignment/
├── doctor-service/           # Repo 1
│   ├── app/{main,models,schemas,crud,database}.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── k8s/{postgres,deployment}.yaml
├── appointment-service/      # Repo 2
│   ├── app/{main,models,schemas,database}.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── k8s/{postgres,deployment}.yaml
├── docker-compose.yaml       # local run of both services
├── Telehealth.postman_collection.json
└── ci-cd-example/github-actions-ci.yaml
```
> For submission, push `doctor-service/` and `appointment-service/` as **two
> separate GitHub repositories**.

---

## 5. Execution Instructions

### A. Quick local test with Docker Compose
```powershell
docker compose up --build
# Doctor Service      -> http://localhost:8001/docs
# Appointment Service -> http://localhost:8002/docs
```

### B. Deploy to Kubernetes (Minikube) — Part 3

1. **Start Minikube**
   ```powershell
   minikube start --driver=docker
   ```

2. **Build images directly into Minikube's Docker** (so no registry is needed)
   ```powershell
   minikube docker-env | Invoke-Expression
   docker build -t doctor-service:1.0 ./doctor-service
   docker build -t appointment-service:1.0 ./appointment-service
   ```

3. **Deploy Doctor Service**
   ```powershell
   kubectl apply -f doctor-service/k8s/postgres.yaml
   kubectl apply -f doctor-service/k8s/deployment.yaml
   ```

4. **Deploy Appointment Service**
   ```powershell
   kubectl apply -f appointment-service/k8s/postgres.yaml
   kubectl apply -f appointment-service/k8s/deployment.yaml
   ```

5. **Verify**
   ```powershell
   kubectl get pods
   kubectl get svc
   ```

6. **Access the Appointment Service (NodePort)**
   ```powershell
   minikube service appointment-service --url
   ```
   Use the returned URL in Postman (e.g. `http://127.0.0.1:3xxxx`).

7. **Kubernetes Dashboard** (take screenshots here)
   ```powershell
   minikube dashboard
   ```

### C. Sample end-to-end flow (Postman / curl)
```powershell
# 1. Create a doctor
curl -X POST http://localhost:8001/doctors -H "Content-Type: application/json" `
  -d '{"name":"Dr. Asha Rao","specialization":"Cardiology","email":"asha@th.com"}'

# 2. Add availability (doctor id = 1)
curl -X POST http://localhost:8001/doctors/1/availability -H "Content-Type: application/json" `
  -d '{"day":"2026-11-20","start_time":"10:00:00","end_time":"10:30:00"}'

# 3. Book appointment (slot id = 1) -> Appointment Service calls Doctor Service
curl -X POST http://localhost:8002/appointments -H "Content-Type: application/json" `
  -d '{"patient_name":"John Doe","patient_email":"john@x.com","doctor_id":1,"slot_id":1}'

# 4. Verify the slot is now booked
curl http://localhost:8001/availability/1
```

---

## 6. Deployment Plan (summary)
1. Containerize each service with its own Dockerfile.
2. Each service + its PostgreSQL run as separate K8s Deployments/Services.
3. `doctor-service` is `ClusterIP` (internal); `appointment-service` is
   `NodePort` (external entry point).
4. Config via ConfigMap, credentials via Secret.
5. 2 replicas per service for scalability; readiness/liveness probes for health.
6. (Optional) GitHub Actions CI builds & pushes images on every push.

---

## 7. GitHub Links
- Doctor Service: _<add link>_
- Appointment Service: _<add link>_

---

## 8. Snapshots to include in the document
- [ ] Postman: create doctor / add availability
- [ ] Postman: book appointment (success response)
- [ ] Postman: slot shows `is_booked: true` after booking
- [ ] `kubectl get pods` / `kubectl get svc` output
- [ ] Kubernetes Dashboard (deployments, pods, services)
- [ ] (Optional) GitHub Actions pipeline run
```

