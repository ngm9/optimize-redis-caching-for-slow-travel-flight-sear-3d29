#!/usr/bin/env bash
set -e

cd /root/task

echo "Starting Docker containers..."
docker-compose -f /root/task/docker-compose.yml up -d

echo "Waiting for Redis to be ready..."
REDIS_CONTAINER=$(docker-compose -f /root/task/docker-compose.yml ps -q redis)

if [ -z "$REDIS_CONTAINER" ]; then
  echo "Redis container not found. Exiting."
  exit 1
fi

REDIS_READY=0
for i in {1..30}; do
  if docker exec "$REDIS_CONTAINER" redis-cli -h 127.0.0.1 -p 6379 ping | grep -q PONG; then
    REDIS_READY=1
    break
  else
    echo "Redis not ready yet (attempt $i)..."
    sleep 2
  fi
done

if [ "$REDIS_READY" -ne 1 ]; then
  echo "Redis did not become ready in time. Exiting."
  exit 1
fi

echo "Redis is ready. Waiting for FastAPI application..."

API_READY=0
for i in {1..30}; do
  if curl -s http://127.0.0.1:8000/health | grep -q '"status":"ok"'; then
    API_READY=1
    break
  else
    echo "FastAPI app not ready yet (attempt $i)..."
    sleep 2
  fi
done

if [ "$API_READY" -ne 1 ]; then
  echo "FastAPI application did not become ready in time. Exiting."
  exit 1
fi

echo "Containers are up and healthy. Application is ready for use."

echo "Current container status:"
docker-compose -f /root/task/docker-compose.yml ps
