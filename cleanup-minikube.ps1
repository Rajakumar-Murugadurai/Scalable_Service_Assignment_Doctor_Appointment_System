<#
    cleanup-minikube.ps1
    Removes all Telehealth resources from the Minikube cluster.

    Usage:
      .\cleanup-minikube.ps1              # delete the app resources only
      .\cleanup-minikube.ps1 -Full        # also stop + delete the whole cluster
#>

param(
    [switch]$Full
)

$ErrorActionPreference = "SilentlyContinue"
$root = $PSScriptRoot

Write-Host ">> Deleting application resources..." -ForegroundColor Cyan
kubectl delete -f (Join-Path $root "appointment-service\k8s\deployment.yaml")
kubectl delete -f (Join-Path $root "appointment-service\k8s\postgres.yaml")
kubectl delete -f (Join-Path $root "doctor-service\k8s\deployment.yaml")
kubectl delete -f (Join-Path $root "doctor-service\k8s\postgres.yaml")

if ($Full) {
    Write-Host ">> Stopping and deleting the Minikube cluster..." -ForegroundColor Yellow
    minikube stop
    minikube delete
}

Write-Host ">> Cleanup done." -ForegroundColor Green

