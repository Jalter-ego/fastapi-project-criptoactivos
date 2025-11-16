import yfinance as yf
import logging
from app.core.config import WINDOW_SIZE

logger = logging.getLogger(__name__)

def get_price_history(symbol: str) -> list[float]:
    """
    Obtiene los últimos N días de precios de cierre usando yfinance.
    """
    try:
        # Descargamos N+15 días para asegurar que tengamos suficientes datos
        data = yf.download(symbol, period=f"{WINDOW_SIZE + 15}d", interval="1d")
        if data.empty:
            logger.error(f"yfinance no devolvió datos para {symbol}")
            return []
        
        price_history = data['Close'].values[-WINDOW_SIZE:]
        
        if len(price_history) < WINDOW_SIZE:
            logger.warning(f"yfinance devolvió solo {len(price_history)} días para {symbol}")
            return [] 

        return price_history.tolist()
        
    except Exception as e:
        logger.error(f"Error al descargar datos de yfinance: {e}")
        return []