#!/bin/bash

# Usar el puerto definido por AWS App Runner o 8000 por defecto
PORT=${PORT:-8000}

# Ejecutar uvicorn con el puerto correcto
exec uvicorn main:app --host 0.0.0.0 --port $PORT
