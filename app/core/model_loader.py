import os
import logging
from stable_baselines3 import PPO
from app.core.config import ASSET_LIST, MODELS_DIR

logger = logging.getLogger(__name__)

# Este diccionario global guardará los modelos cargados
MODELS = {}

def load_all_models():
    """Itera sobre la ASSET_LIST y carga los modelos de IA en memoria."""
    logger.info("Iniciando carga de modelos de IA...")
    
    for asset_id in ASSET_LIST:
        # Convierte "BTC-USD" a "ppo_btc_model_v2.zip"
        model_name = f"ppo_{asset_id.replace('-', '_').lower()}_model_v2.zip"
        model_path = os.path.join(MODELS_DIR, model_name)
        
        if os.path.exists(model_path):
            try:
                MODELS[asset_id] = PPO.load(model_path)
                logger.info(f"¡Modelo {asset_id} cargado desde {model_path}!")
            except Exception as e:
                logger.error(f"Error al cargar {model_path}: {e}")
        else:
            logger.warning(f"ADVERTENCIA: No se encontró modelo para {asset_id} en {model_path}")