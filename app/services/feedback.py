import requests
import logging
from app.core.config import NESTJS_FEEDBACK_URL

logger = logging.getLogger(__name__)

def send_feedback_to_nestjs(portafolio_id: str, message: str, type: str):
    """Función helper para enviar el feedback de vuelta a NestJS."""
    try:
        payload = {
            "portafolioId": portafolio_id,
            "message": message,
            "type": type
        }
        print(f"Enviando feedback a NestJS: {payload}") # Útil para debug
        response = requests.post(NESTJS_FEEDBACK_URL, json=payload, timeout=5)
        response.raise_for_status() 
        logger.info(f"Feedback enviado para {portafolio_id}: {type}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error enviando feedback a NestJS: {e}")
    except Exception as e:
        logger.error(f"Error inesperado en send_feedback_to_nestjs: {e}")