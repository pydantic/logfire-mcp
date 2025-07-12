#!/bin/bash
set -e

# Build multi-platform Docker image
docker buildx create --use --name mcp-builder || true

# Build for both amd64 and arm64
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag mcp/logfire:latest \
  --tag mcp/logfire:$(git describe --tags --always) \
  --push \
  .

echo "Docker image built and pushed successfully!"