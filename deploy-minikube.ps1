<#
    deploy-minikube.ps1
    One-command deployment of the Telehealth microservices to a local Minikube cluster.

    What it does:
      1. Starts Minikube (docker driver) if not already running
      2. Enables the dashboard + metrics-server addons
      3. Injects your Docker Hub username into the Deployment manifests
      4. Applies all manifests (databases first, then services)
      5. Waits for every Deployment to become Ready
      6. Prints the Appointment Service URL and how to open the dashboard

    Usage:
      .\deploy-minikube.ps1 -DockerHubUser <your-dockerhub-username>
      .\deploy-minikube.ps1 -DockerHubUser myuser -Tag 1.0

    Prerequisites (one-time):
      winget install Kubernetes.minikube
      winget install Kubernetes.kubectl
      A running container runtime for the minikube "docker" driver.
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$DockerHubUser,

    [string]$Tag = "1.0"
)

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

function Require-Command($name, $hint) {
    if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
        Write-Error "'$name' not found. $hint"
        exit 1
    }
}

Require-Command minikube "Install with: winget install Kubernetes.minikube"
Require-Command kubectl  "Install with: winget install Kubernetes.kubectl"

# 1. Start Minikube if it is not already running
$status = (& minikube status --format '{{.Host}}' 2>$null)
if ($status -ne "Running") {
    Write-Host ">> Starting Minikube (docker driver)..." -ForegroundColor Cyan
    minikube start --driver=docker
} else {
    Write-Host ">> Minikube already running." -ForegroundColor Green
}

# 2. Enable dashboard + metrics (used for screenshots and HPA/metrics)
Write-Host ">> Enabling dashboard + metrics-server addons..." -ForegroundColor Cyan
minikube addons enable dashboard | Out-Null
minikube addons enable metrics-server | Out-Null

# 3. Build manifests with the real Docker Hub username injected.
#    We write temp copies so the original files keep the placeholder.
$tmp = Join-Path $env:TEMP "th-k8s"
if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
New-Item -ItemType Directory -Path $tmp | Out-Null

$deployments = @(
    "doctor-service\k8s\deployment.yaml",
    "appointment-service\k8s\deployment.yaml"
)
foreach ($rel in $deployments) {
    $src = Join-Path $root $rel
    $dstName = ($rel -replace '[\\]', '_')
    $dst = Join-Path $tmp $dstName
    (Get-Content $src -Raw).Replace("YOUR_DOCKERHUB_USERNAME", $DockerHubUser).Replace(":1.0", ":$Tag") |
        Set-Content $dst -Encoding UTF8
}

# 4. Apply manifests: databases + config first, then the service deployments.
Write-Host ">> Applying Doctor Service database + config..." -ForegroundColor Cyan
kubectl apply -f (Join-Path $root "doctor-service\k8s\postgres.yaml")

Write-Host ">> Applying Appointment Service database + config..." -ForegroundColor Cyan
kubectl apply -f (Join-Path $root "appointment-service\k8s\postgres.yaml")

Write-Host ">> Applying Doctor Service deployment..." -ForegroundColor Cyan
kubectl apply -f (Join-Path $tmp "doctor-service_k8s_deployment.yaml")

Write-Host ">> Applying Appointment Service deployment..." -ForegroundColor Cyan
kubectl apply -f (Join-Path $tmp "appointment-service_k8s_deployment.yaml")

# 5. Wait for rollouts
Write-Host ">> Waiting for all deployments to become Ready..." -ForegroundColor Cyan
$deploys = @("doctor-postgres", "appointment-postgres", "doctor-service", "appointment-service")
foreach ($d in $deploys) {
    kubectl rollout status deployment/$d --timeout=180s
}

# 6. Summary
Write-Host "`n==================== DEPLOYMENT COMPLETE ====================" -ForegroundColor Green
kubectl get pods
Write-Host ""
kubectl get svc
Write-Host ""
Write-Host "Appointment Service (NodePort) URL:" -ForegroundColor Yellow
minikube service appointment-service --url
Write-Host ""
Write-Host "Open the Kubernetes dashboard (for screenshots) with:" -ForegroundColor Yellow
Write-Host "   minikube dashboard"
Write-Host "============================================================" -ForegroundColor Green

