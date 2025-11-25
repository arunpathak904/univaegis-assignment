#!/bin/bash
set -euo pipefail

WORKDIR="$HOME/univaegis-assignment"
ENV_FILE="$WORKDIR/.env"

# 1) ensure workdir exists
mkdir -p "$WORKDIR"
cd "$WORKDIR"

# 2) Create .env from environment variables (these are passed from GitHub Actions)
#    If .env already exists on server and you want to preserve, remove the following block.
cat > "$ENV_FILE" <<'EOF'
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT}

DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
DJANGO_DEBUG=${DJANGO_DEBUG}
DJANGO_ALLOWED_HOSTS=${DJANGO_ALLOWED_HOSTS}

BACKEND_IMAGE=${BACKEND_IMAGE}
FRONTEND_IMAGE=${FRONTEND_IMAGE}

HOST_BACKEND_PORT=${HOST_BACKEND_PORT}
CONTAINER_BACKEND_PORT=${CONTAINER_BACKEND_PORT}
HOST_FRONTEND_PORT=${HOST_FRONTEND_PORT}
CONTAINER_FRONTEND_PORT=${CONTAINER_FRONTEND_PORT}
EOF

echo "[deploy] .env written to $ENV_FILE"
cat "$ENV_FILE"

# 3) Pull images and recreate containers
echo "[deploy] docker compose pull"
docker compose pull || echo "[deploy] pull warning - continuing"

echo "[deploy] docker compose up -d --remove-orphans"
docker compose up -d --remove-orphans

# 4) Run migrations & collectstatic (best-effort)
echo "[deploy] Running migrate and collectstatic (best-effort)"
docker compose exec -T backend python manage.py migrate --noinput || echo "[deploy] migrate may fail if backend not ready"
docker compose exec -T backend python manage.py collectstatic --noinput || echo "[deploy] collectstatic done or not needed"

echo "[deploy] Deployment finished."
