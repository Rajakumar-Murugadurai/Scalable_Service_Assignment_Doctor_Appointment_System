#!/usr/bin/env bash
# Build both microservice images and push them to Docker Hub.
# Run this from INSIDE WSL2 Ubuntu, from the project root.
#
# Usage:
#   chmod +x build-and-push.sh
#   ./build-and-push.sh <your-dockerhub-username>
#
set -e

if [ -z "$1" ]; then
  echo "Usage: ./build-and-push.sh <dockerhub-username>"
  exit 1
fi

USER="$1"
TAG="1.0"

echo ">> Logging in to Docker Hub (enter your password / access token)"
docker login -u "$USER"

echo ">> Building doctor-service"
docker build -t "$USER/doctor-service:$TAG" ./doctor-service

echo ">> Building appointment-service"
docker build -t "$USER/appointment-service:$TAG" ./appointment-service

echo ">> Pushing images to Docker Hub"
docker push "$USER/doctor-service:$TAG"
docker push "$USER/appointment-service:$TAG"

echo ">> Done. Images available at:"
echo "   https://hub.docker.com/r/$USER/doctor-service"
echo "   https://hub.docker.com/r/$USER/appointment-service"

