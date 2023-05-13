#!/bin/bash

# Stop and remove existing containers
docker stop model-service app
docker rm model-service app

# Remove existing image
docker rmi ghcr.io/remla23-team2/model-service

# Rebuild image
docker build -t ghcr.io/remla23-team2/model-service .

# Run containers
docker run -d -p 8080:8080 --name model-service ghcr.io/remla23-team2/model-service
docker run -d -p 3000:3000 --name app --link model-service:api app

