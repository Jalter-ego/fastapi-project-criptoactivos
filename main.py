from fastapi import FastAPI
from app.api.api import api_router
from app.core.model_loader import load_all_models
import logging

# Configura el logging principal
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Simulador Cripto IA")

@app.on_event("startup")
def on_startup():
    """Al iniciar, carga los modelos de IA."""
    load_all_models()

# Incluye todos los endpoints de la API (v1)
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"status": "Servicio de IA Activo"}

# uvicorn app.main:app --reload --host 0.0.0.0 --port 8000