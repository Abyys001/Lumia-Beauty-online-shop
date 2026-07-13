#!/usr/bin/env bash
# =============================================================================
# Build the production images and push them to your registry.
# Run ON YOUR MACHINE (or CI), after `docker login`:
#   ./scripts/build-and-push.sh
#
# Override the target with env vars, e.g.:
#   REGISTRY=docker.io/youruser TAG=v1 ./scripts/build-and-push.sh
#
# The image names default to the ones referenced in docker-compose.yml.
# =============================================================================
set -euo pipefail

REGISTRY="${REGISTRY:-docker.io/siavashdev}"
TAG="${TAG:-latest}"

BACKEND_IMAGE="${BACKEND_IMAGE:-$REGISTRY/lumia-backend:$TAG}"
FRONTEND_IMAGE="${FRONTEND_IMAGE:-$REGISTRY/lumia-frontend:$TAG}"

# VPS is almost always linux/amd64. If you build on Apple Silicon, uncomment:
# PLATFORM="--platform linux/amd64"
PLATFORM="${PLATFORM:-}"

cd "$(dirname "$0")/.."

echo "### Building backend  -> $BACKEND_IMAGE"
docker build $PLATFORM -t "$BACKEND_IMAGE" ./backend

echo "### Building frontend -> $FRONTEND_IMAGE  (frontend/Dockerfile.prod)"
docker build $PLATFORM -f ./frontend/Dockerfile.prod -t "$FRONTEND_IMAGE" ./frontend

echo "### Pushing ..."
docker push "$BACKEND_IMAGE"
docker push "$FRONTEND_IMAGE"

cat <<EOF

### Done.
On the server (.env must set BACKEND_IMAGE / FRONTEND_IMAGE to match if you
changed REGISTRY/TAG — defaults already match .env.vps):

    docker compose pull
    docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
EOF
