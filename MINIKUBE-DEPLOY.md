# Part 3 — Minikube Deployment Guide (Telehealth Microservices)

This guide covers deploying both microservices to a local **Minikube** Kubernetes
cluster and capturing the screenshots required for the assignment document.

> Replace `YOUR_DOCKERHUB_USERNAME` everywhere below with your real Docker Hub username.

---

## 1. Prerequisites (one-time)

Install the Kubernetes tools from PowerShell:

```powershell
winget install Kubernetes.minikube
winget install Kubernetes.kubectl
```

Close and reopen PowerShell so the PATH updates, then verify:

```powershell
minikube version
kubectl version --client
```

You also need the two images pushed to Docker Hub (see `build-and-push.ps1` /
`build-and-push.sh`), so the cluster can pull:

- `YOUR_DOCKERHUB_USERNAME/doctor-service:1.0`
- `YOUR_DOCKERHUB_USERNAME/appointment-service:1.0`

---

## 2. One-command deploy (recommended)

From the project root:

```powershell
.\deploy-minikube.ps1 -DockerHubUser YOUR_DOCKERHUB_USERNAME
```

The script will:
1. Start Minikube (docker driver)
2. Enable the **dashboard** and **metrics-server** addons
3. Inject your Docker Hub username into the Deployment manifests
4. Apply the databases/config first, then the service deployments
5. Wait for every Deployment to become Ready
6. Print the Appointment Service URL and dashboard command

---

## 3. Manual deploy (if you prefer running each step)

```powershell
# Start the cluster
minikube start --driver=docker

# Enable dashboard for screenshots
minikube addons enable dashboard
minikube addons enable metrics-server

# Edit the two deployment.yaml files and replace YOUR_DOCKERHUB_USERNAME first.

# Doctor Service (DB + config, then app)
kubectl apply -f doctor-service/k8s/postgres.yaml
kubectl apply -f doctor-service/k8s/deployment.yaml

# Appointment Service (DB + config, then app)
kubectl apply -f appointment-service/k8s/postgres.yaml
kubectl apply -f appointment-service/k8s/deployment.yaml

# Watch until every pod is Running
kubectl get pods -w
```

---

## 4. Verify the deployment

```powershell
kubectl get deployments
kubectl get pods -o wide
kubectl get svc
```

Expected: `doctor-service` (2 replicas), `appointment-service` (2 replicas),
`doctor-postgres` (1), `appointment-postgres` (1) — all `Running`.

Get the externally reachable URL for the Appointment Service (NodePort 30080):

```powershell
minikube service appointment-service --url
```

Open `<that-url>/docs` in a browser to confirm the Swagger UI loads.

---

## 5. Kubernetes Dashboard (required screenshot)

```powershell
minikube dashboard
```

A browser opens automatically. Capture screenshots of:
- **Workloads → Deployments** (shows 4 deployments, replica counts)
- **Workloads → Pods** (all green/Running)
- **Service → Services** (ClusterIP + NodePort entries)

---

## 6. End-to-end test with Postman (required screenshots)

1. Import `Telehealth.postman_collection.json`.
2. Set the collection variable `appointmentUrl` to the NodePort URL from step 4,
   and `doctorUrl` via `minikube service doctor-service --url` (or use port-forward).
3. Run the requests in order and screenshot each response:

| # | Request | Service | Purpose |
|---|---------|---------|---------|
| 1 | `POST /doctors` | Doctor | Create a doctor |
| 2 | `POST /doctors/1/availability` | Doctor | Add an availability slot |
| 3 | `GET /availability/1` | Doctor | Confirm slot is OPEN |
| 4 | `POST /appointments` | Appointment | Book — calls Doctor Service (inter-service REST) |
| 5 | `GET /availability/1` | Doctor | Confirm slot now BOOKED |
| 6 | `GET /appointments` | Appointment | List appointments |

Request #4 demonstrates the **inter-service collaboration** (Appointment Service
→ Doctor Service over REST), which is a key grading point for Part 2.

If you need to reach the Doctor Service directly without a NodePort:

```powershell
kubectl port-forward svc/doctor-service 8001:8000
# now http://localhost:8001/docs works
```

---

## 7. Useful troubleshooting commands

```powershell
kubectl describe pod <pod-name>          # why a pod isn't starting
kubectl logs deployment/doctor-service   # app logs
kubectl logs deployment/appointment-service
kubectl get events --sort-by=.lastTimestamp
```

Common issues:
- **ImagePullBackOff** → image name/username wrong, or image not pushed to Docker Hub (make it a public repo).
- **CrashLoopBackOff on a service** → its Postgres pod isn't Ready yet; wait and it self-recovers.

---

## 8. Cleanup

```powershell
.\cleanup-minikube.ps1          # remove app resources
.\cleanup-minikube.ps1 -Full    # also stop + delete the cluster
```

---

## 9. What this satisfies in the rubric (Part 3 — 7 points)

- ✅ Each service in its **own Docker container** (separate images on Docker Hub)
- ✅ Deployed to a **Kubernetes cluster** (Minikube)
- ✅ **Minikube cluster** running locally
- ✅ **Kubernetes dashboard** accessed and analyzed (screenshots)
- ✅ Database-per-service, ConfigMaps, Secrets, health probes, 2 replicas (scalability)

