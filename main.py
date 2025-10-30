from fastapi import FastAPI
import requests
import logging
import os


app = FastAPI()

# Configura un logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

NESTJS_FEEDBACK_URL = os.environ.get("NESTJS_FEEDBACK_URL", "http://localhost:3000/feedback")
SIMULATED_FEE_RATE = 0.005  # 0.5% de comisión por transacción
SLIPPAGE_TOLERANCE = 0.001 # 0.1% de tolerancia al deslizamiento

@app.get("/")
def read_root():
    return {"Hello": "World"}

def send_feedback_to_nestjs(portafolio_id: str, message: str, type: str):
    """Función helper para enviar el feedback de vuelta a NestJS."""
    try:
        payload = {
            "portafolioId": portafolio_id,
            "message": message,
            "type": type
        }
        print(f"Enviando feedback a NestJS: {payload}")
        response = requests.post(NESTJS_FEEDBACK_URL, json=payload, timeout=5)
        response.raise_for_status() # Lanza un error si la API de NestJS falla
        logger.info(f"Feedback enviado para {portafolio_id}: {type}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error enviando feedback a NestJS: {e}")
    except Exception as e:
        logger.error(f"Error inesperado en send_feedback_to_nestjs: {e}")

@app.post("/analyze-trade")
async def analyze_trade(data: dict):
    portafolio = data.get("portafolio", {})
    transaction = data.get("transaction", {})
    market_data = data.get("marketData", {})
    
    portafolio_id = portafolio.get("id")
    if not portafolio_id:
        return {"error": "No portafolio ID provided"}

    # --- Ejecutamos los 3 análisis (HU7, 8, 9) ---
    
    # HU8: Generación de Alertas de Riesgo
    analyze_risk(portafolio, transaction, market_data)
    
    # HU9: Análisis de Costos y Slippage (Deslizamiento)
    analyze_costs_and_slippage(transaction, market_data)

    # HU7: Sistema de Retroalimentación Activa (Sesgos)
    analyze_behavior(transaction, market_data)

    return {"status": "analysis_queued"}

# --- LÓGICA DE "IA" (Iniciaremos con reglas/heurísticas) ---

def analyze_risk(portafolio: dict, transaction: dict, market_data: dict):
    """HU8: Analiza la sobre-concentración y el riesgo 'All-In'."""
    portafolio_id = portafolio.get("id")
    holdings = portafolio.get("holdings", [])
    cash_after_tx = portafolio.get("cash", 0)
    tx_type = transaction.get("type")
    
    # --- 1. Lógica 'All-In' (Gastar todo el efectivo) ---
    if tx_type == "BUY":
        tx_cost = transaction.get("amount", 0) * transaction.get("price", 0)
        cash_before_tx = cash_after_tx + tx_cost
        
        if cash_before_tx > 0 and (tx_cost / cash_before_tx) > 0.90:
            msg = (f"¡Alerta de Riesgo! Usaste el { (tx_cost / cash_before_tx) * 100:.0f}% de tu "
                   f"efectivo disponible en una sola compra de {transaction.get('activeSymbol')}. "
                   "Evita ir 'All-In' para gestionar mejor el riesgo.")
            send_feedback_to_nestjs(portafolio_id, msg, "RISK_ALERT")
            
    # --- 2. Revisar concentración ---
    
    # 👇 --- CAMBIO 3: Añade la lógica de cálculo que faltaba ---
    total_value = cash_after_tx
    asset_values = {}

    # Calcular el valor total del portafolio usando los datos de mercado
    for holding in holdings:
        symbol = holding.get("activeSymbol")
        quantity = holding.get("quantity", 0)
        
        if symbol in market_data:
            price = float(market_data[symbol].get("price", 0))
            value = quantity * price
            asset_values[symbol] = value
            total_value += value # Sumamos el valor de los activos al efectivo
            
    if total_value == 0:
        return # No se puede dividir por cero

    # Ahora esta lógica SÍ funcionará
    for symbol, value in asset_values.items():
        concentration = (value / total_value) * 100
        if concentration > 60: # Regla: > 60% en un activo es riesgoso
            msg = f"¡Alerta de Riesgo! Tienes un {concentration:.0f}% de tu portafolio en {symbol}. Considera diversificar."
            send_feedback_to_nestjs(portafolio_id, msg, "RISK_ALERT")



def analyze_costs_and_slippage(transaction: dict, market_data: dict):
    """HU9: Analiza costos (comisión simulada) y slippage."""
    portafolio_id = transaction.get("portafolioId")
    symbol = transaction.get("activeSymbol")
    tx_type = transaction.get("type")
    tx_price = transaction.get("price", 0)
    tx_amount = transaction.get("amount", 0)

    # --- 1. Análisis de Comisión (Simulada) ---
    total_cost_usd = tx_amount * tx_price
    commission_paid = total_cost_usd * SIMULATED_FEE_RATE
    
    # Esta es una notificación informativa, no una alerta de error
    msg_cost = (f"Análisis de Costos: Tu transacción de {symbol} generó "
                f"una comisión simulada de ${commission_paid:.2f} (0.5%).")
    # (Descomenta si quieres enviar este feedback informativo siempre)
    # send_feedback_to_nestjs(portafolio_id, msg_cost, "COST_ANALYSIS")

    # --- 2. Análisis de Slippage (Deslizamiento) ---
    if symbol not in market_data:
        return # No podemos comparar si no hay datos de mercado

    ticker = market_data[symbol]
    slippage = 0.0

    if tx_type == "BUY":
        best_ask = float(ticker.get("best_ask", tx_price)) # Precio de venta
        if tx_price > best_ask:
            slippage = tx_price - best_ask
    
    elif tx_type == "SELL":
        best_bid = float(ticker.get("best_bid", tx_price)) # Precio de compra
        if tx_price < best_bid:
            slippage = best_bid - tx_price
            
    # Si hubo un deslizamiento negativo de más de 0.1%
    if slippage > 0 and (slippage / tx_price) > SLIPPAGE_TOLERANCE:
        slippage_percent = (slippage / tx_price) * 100
        msg_slip = (f"Análisis de Costos: Tu {tx_type} de {symbol} tuvo un 'slippage' (deslizamiento) "
                    f"negativo del {slippage_percent:.2f}%. Pagaste un precio peor que el "
                    "mejor precio disponible en el mercado.")
        send_feedback_to_nestjs(portafolio_id, msg_slip, "COST_ANALYSIS")



def analyze_behavior(transaction: dict, market_data: dict):
    """HU7: Analiza sesgos conductuales (FOMO y Venta de Pánico)."""
    portafolio_id = transaction.get("portafolioId")
    symbol = transaction.get("activeSymbol")
    tx_type = transaction.get("type")
    
    if symbol not in market_data:
        return # No hay datos para analizar

    ticker = market_data[symbol]
    price_change_24h = float(ticker.get("price_percent_chg_24_h", 0))

    # --- 1. Lógica de FOMO (Comprar alto) ---
    if tx_type == "BUY":
        # (Usa un valor bajo para probar, luego cámbialo a 20 o 30)
        if price_change_24h > 0: # <-- CAMBIA ESTO A 20 PARA PRODUCCIÓN
            msg_fomo = (f"Análisis Conductual: Compraste {symbol} después de que subió un "
                        f"{price_change_24h:.2f}% en 24 horas. ¿Podría ser FOMO (Miedo a Quedarse Fuera)?")
            send_feedback_to_nestjs(portafolio_id, msg_fomo, "BEHAVIORAL_NUDGE")

    # --- 2. NUEVA LÓGICA: Venta de Pánico (Vender bajo) ---
    elif tx_type == "SELL":
        # (Usa un valor bajo para probar, luego cámbialo a -20)
        if price_change_24h < 0: # <-- CAMBIA ESTO A -20 PARA PRODUCCIÓN
            msg_panic = (f"Análisis Conductual: Vendiste {symbol} después de que cayó un "
                         f"{price_change_24h:.2f}% en 24 horas. ¿Estás seguro de que no es "
                         "una Venta de Pánico?")
            send_feedback_to_nestjs(portafolio_id, msg_panic, "BEHAVIORAL_NUDGE")


