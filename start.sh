#!/bin/bash
set -e

# Use Railway's PORT or default to 8080
PORT=${PORT:-8080}

echo "Starting Sales API on port $PORT..."
exec uvicorn main:app --host 0.0.0.0 --port $PORT
