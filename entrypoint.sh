#!/usr/bin/env sh
set -e

# 1) Instalamos/actualizamos deps (se lee /app/requirements.txt montado por docker-compose)
pip install --upgrade pip
pip install --no-cache-dir -r /app/requirements.txt

# 2) Ejecutamos el comando que reciba (por defecto Uvicorn)
exec "$@"
