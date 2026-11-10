#!/usr/bin/env bash
#
# wsl-deploy.sh
# Full Part-3 deployment of the Telehealth microservices to Minikube,
# running entirely inside WSL2 Ubuntu WITHOUT Docker Desktop and WITHOUT sudo.
#
# It:
#   1. Installs kubectl + minikube into ~/.local/bin (no root needed)
#   2. Starts a Minikube cluster using the docker drive
#   3. Enables the dashboard + metrics-server addons
#   4. Builds both service images directly into Minikube's Docker daemon
#   5. Applies the Kubernetes manifests (databases first, then services)
#   6. Waits for every deployment to become Ready and prints access info
#
# Usage (from a WSL terminal, or via: wsl -d Ubuntu-20.04 -- bash <path>):
#   bash wsl-deploy.sh
#
set -euo pipefail

PROJ="/mnt/c/Users/r.murugadurai/PycharmProjects/SS_Assignment"
BIN="$HOME/.local/bin"
export PATH="$BIN:$PATH"
mkdir -p "$BIN"

echo "==> [1/6] Ensuring kubectl + minikube are installed (no sudo)"

if ! command -v kubectl >/dev/null 2>&1; then
  echo "    installing kubectl..."
  Kver="$(curl -L -s https://dl.k8s.io/release/stable.txt)"
  curl -L -s -o "$BIN/kubectl" "https://dl.k8s.io/release/${Kver}/bin/linux/amd64/kubectl"
  chmod +x "$BIN/kubectl"
fi
echo "    kubectl: $(command -v kubectl)"

if ! command -v minikube >/dev/null 2>&1; then
  echo "    installing minikube..."
  curl -L -s -o "$BIN/minikube" "https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64"
  chmod +x "$BIN/minikube"
fi
echo "    minikube: $(command -v minikube)"

echo "==> [2/6] Starting Minikube (docker driver)"
# Make sure the docker daemon is up (works without sudo for this user).
if ! docker info >/dev/null 2>&1; then
  echo "    docker daemon not reachable; trying to start it..."
  sudo service docker start || true
  sleep 3
fi

if [ "$(minikube status --format '{{.Host}}' 2>/dev/null || true)" != "Running" ]; then
  minikube start --driver=docker --wait=all
else
  echo "    minikube already running."
fi

echo "==> [3/6] Enabling dashboard + metrics-server addons"
minikube addons enable dashboard  >/dev/null
minikube addons enable metrics-server >/dev/null

echo "==> [4/6] Building images (host Docker) and loading them into Minikube"
# Build with the host Docker daemon (works without sudo for this user).
docker build -t doctor-service:1.0      "$PROJ/doctor-service"
docker build -t appointment-service:1.0 "$PROJ/appointment-service"
# Load the images into the Minikube node. This works with the containerd
# runtime too, unlike the "minikube docker-env" approach.
minikube image load doctor-service:1.0
minikube image load appointment-service:1.0

echo "==> [5/6] Applying Kubernetes manifests"
TMP="$(mktemp -d)"
# Rewrite the deployment manifests to use the locally-built images
# (replace the Docker Hub placeholder and force local image use).
sed -e 's#YOUR_DOCKERHUB_USERNAME/doctor-service:1.0#doctor-service:1.0#' \
    -e 's#imagePullPolicy: Always#imagePullPolicy: IfNotPresent#' \
    "$PROJ/doctor-service/k8s/deployment.yaml" > "$TMP/doctor-deployment.yaml"
sed -e 's#YOUR_DOCKERHUB_USERNAME/appointment-service:1.0#appointment-service:1.0#' \
    -e 's#imagePullPolicy: Always#imagePullPolicy: IfNotPresent#' \
    "$PROJ/appointment-service/k8s/deployment.yaml" > "$TMP/appointment-deployment.yaml"

# Databases + config/secrets first
kubectl apply -f "$PROJ/doctor-service/k8s/postgres.yaml"
kubectl apply -f "$PROJ/appointment-service/k8s/postgres.yaml"
# Then the application deployments
kubectl apply -f "$TMP/doctor-deployment.yaml"
kubectl apply -f "$TMP/appointment-deployment.yaml"

echo "==> [6/6] Waiting for deployments to become Ready"
for d in doctor-postgres appointment-postgres doctor-service appointment-service; do
  kubectl rollout status "deployment/$d" --timeout=240s
done

echo ""
echo "==================== DEPLOYMENT COMPLETE ===================="
kubectl get pods -o wide
echo ""
kubectl get svc
echo ""
echo "Appointment Service URL (NodePort):"
minikube service appointment-service --url
echo ""
echo "Open the Kubernetes dashboard with:   minikube dashboard --url"
echo "============================================================"

