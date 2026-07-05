#!/usr/bin/env bash
set -e

echo "Stopping and removing containers, networks, and volumes for task..."

docker-compose -f /root/task/docker-compose.yml down --volumes --remove-orphans || true

echo "Removing task-related images (application and redis:7-alpine if present)..."
IMAGES=$(docker images -q | grep -E 'redis:7-alpine' || true)
if [ -n "$IMAGES" ]; then
  docker rmi -f $IMAGES || true
fi

APP_IMAGES=$(docker images -q | head -n 20 || true)
if [ -n "$APP_IMAGES" ]; then
  docker rmi -f $APP_IMAGES || true
fi

echo "Pruning unused Docker resources (containers, images, networks, volumes)..."
docker system prune -a --volumes -f || true

echo "Deleting task directory at /root/task..."
rm -rf /root/task || true

echo "Cleanup completed successfully! Droplet is now clean."
