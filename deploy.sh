#!/bin/bash

set -e

echo ""
echo "Deploy started at $(date + "%Y-%m-%d %H:%M:%S")"

cd "$(dirname "$0")"

echo "Pulling latest changes from git"
git pull origin main

echo "Changes pulled"

echo "Stopping and removing old containers"
sudo docker compose down

echo "Building and starting updated containers"
sudo docker compose up --build -d

echo "Deploy successfully completed at $(date + "%Y-%m-%d %H:%M:%S")"