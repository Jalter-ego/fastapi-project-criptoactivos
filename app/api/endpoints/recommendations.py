from fastapi import APIRouter
import numpy as np
import logging
from app.core.model_loader import MODELS
from app.core.config import WINDOW_SIZE
from app.services.market import get_price_history
from app.schemas.recommendation import PredictionState

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/get-recommendation/{asset_id}")
async def get_recommendation(asset_id: str, state: PredictionState):
    """
    Recibe el estado del usuario desde NestJS, obtiene los datos del mercado
    y devuelve una recomendación del modelo de RL.
    """
    logger.info(f"Recibida solicitud de recomendación para: {asset_id}")

    if asset_id not in MODELS:
        logger.warning(f"No hay un modelo entrenado para {asset_id}.")
        return {"recommendation": "NO_MODEL"}

    try:
        model = MODELS[asset_id]
        
        price_history = get_price_history(asset_id)
        
        if len(price_history) != WINDOW_SIZE:
            logger.error(f"No se pudo obtener el historial de precios completo para {asset_id}")
            return {"recommendation": "ERROR_MARKET_DATA"}

        obs_vector = np.concatenate(
            (
                np.array([state.balance, state.crypto_held], dtype=np.float32).flatten(),
                np.array(price_history, dtype=np.float32).flatten()
            )
        )

        if obs_vector.shape[0] != (2 + WINDOW_SIZE):
             raise ValueError(f"El vector de observación tiene una forma incorrecta: {obs_vector.shape}")

        action, _ = model.predict(obs_vector, deterministic=True)
        
        if action == 1 and state.balance > 0:
            recommendation = "BUY"
        elif action == 2 and state.crypto_held > 0:
            recommendation = "SELL"
        else:
            recommendation = "HOLD"
            
        logger.info(f"Recomendación para {asset_id}: {recommendation}")
        return {"recommendation": recommendation}

    except Exception as e:
        logger.error(f"Error durante la predicción: {e}")
        return {"recommendation": "ERROR", "detail": str(e)}