FROM python:3.11-slim

# Dependencias necesarias para ML (scikit-learn, numpy, pandas, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de la app
WORKDIR /app

# Copiar requirements e instalar dependencias
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del proyecto
COPY . .

# Definir el puerto (App Runner usa esta variable)
ENV PORT=8000

EXPOSE $PORT

# CMD final (sin start.sh)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
