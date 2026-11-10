<#
    build-and-push.ps1
    Build both microservice images and push them to Docker Hub from PowerShell.
    Run from the project root.

    Usage:
        .\build-and-push.ps1 -DockerHubUser <your-dockerhub-username>
        .\build-and-push.ps1 -DockerHubUser myuser -Tag 1.0

    Prerequisite: Docker Engine must be installed and running (see PHASE 0 below).
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$DockerHubUser,

    [string]$Tag = "1.0"
)

$ErrorActionPreference = "Stop"

# Make sure docker is available
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "docker command not found. Install Docker first (see README / PHASE 0)."
    exit 1
}

Write-Host ">> Logging in to Docker Hub (enter your password / access token)" -ForegroundColor Cyan
docker login -u $DockerHubUser

Write-Host ">> Building doctor-service" -ForegroundColor Cyan
docker build -t "$DockerHubUser/doctor-service:$Tag" .\doctor-service

Write-Host ">> Building appointment-service" -ForegroundColor Cyan
docker build -t "$DockerHubUser/appointment-service:$Tag" .\appointment-service

Write-Host ">> Pushing images to Docker Hub" -ForegroundColor Cyan
docker push "$DockerHubUser/doctor-service:$Tag"
docker push "$DockerHubUser/appointment-service:$Tag"

Write-Host ">> Done. Images available at:" -ForegroundColor Green
Write-Host "   https://hub.docker.com/r/$DockerHubUser/doctor-service"
Write-Host "   https://hub.docker.com/r/$DockerHubUser/appointment-service"

