import os

# --- Configuración de NestJS ---
NESTJS_FEEDBACK_URL = os.environ.get("NESTJS_FEEDBACK_URL", "http://localhost:3000/feedback")

# --- Configuración de Heurísticas (Sprint 2) ---
SIMULATED_FEE_RATE = 0.005  # 0.5% de comisión por transacción
SLIPPAGE_TOLERANCE = 0.0005 # 0.1% de tolerancia al deslizamiento

# --- Configuración de RL (Sprint 3) ---
WINDOW_SIZE = 30 
MODELS_DIR = "models"
ASSET_LIST = [
    "BTC-USD",
    "ETH-USD",
    "USDT-USD",
    "XRP-USD",
    "SOL-USD",
    "DOGE-USD",
    "ADA-USD",
    "LINK-USD",
    "AVAX-USD",
    "XLM-USD",
    "SUI-USD",
    "BCH-USD",
    "HBAR-USD",
    "LTC-USD",
    "SHIB-USD",
    "CRO-USD",
    "DOT-USD",
    "ENA-USD",
    "TAO-USD",
    "ETC-USD",
]