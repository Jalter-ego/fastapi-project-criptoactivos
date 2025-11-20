# Etapa de construcción
FROM python:3.11-slim as builder

# Instalar dependencias del sistema para las librerías de ML
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Crear entorno virtual
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Etapa de producción
FROM python:3.11-slim

# Instalar runtime dependencies
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copiar entorno virtual de la etapa de construcción
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Crear directorio de la aplicación
WORKDIR /app

# Copiar código de la aplicación
COPY . .

# Exponer puerto (App Runner usa PORT, default 8000)
ENV PORT=8000
EXPOSE $PORT

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
