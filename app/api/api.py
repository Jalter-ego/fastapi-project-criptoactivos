from fastapi import APIRouter
from app.api.endpoints import heuristics, recommendations

api_router = APIRouter()

# Incluye el router del Sprint 2
api_router.include_router(heuristics.router, tags=["Heuristics (Sprint 2)"])

# Incluye el router del Sprint 3
api_router.include_router(recommendations.router, tags=["Recommendations (Sprint 3)"])