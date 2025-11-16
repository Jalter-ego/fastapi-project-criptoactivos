from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
from app.services.feedback import send_feedback_to_nestjs
from app.core.config import SIMULATED_FEE_RATE, SLIPPAGE_TOLERANCE

router = APIRouter()

class HeuristicInput(BaseModel):
    portafolio: Dict[str, Any]
    transaction: Dict[str, Any]
    market_data: Dict[str, Any]

@router.post("/analyze-trade")
async def analyze_trade(data: HeuristicInput):
    portafolio = data.portafolio
    transaction = data.transaction
    market_data = data.market_data
    
    portafolio_id = portafolio.get("id")
    if not portafolio_id:
        return {"error": "No portafolio ID provided"}
    
    # HU8: Generación de Alertas de Riesgo
    _analyze_risk(portafolio, transaction, market_data)
    
    # HU9: Análisis de Costos y Slippage
    _analyze_costs_and_slippage(transaction, market_data)

    # HU7: Sistema de Retroalimentación Activa
    _analyze_behavior(transaction, market_data)

    return {"status": "analysis_queued"}



def _analyze_risk(portafolio: dict, transaction: dict, market_data: dict):
    """HU8: Analiza la sobre-concentración y el riesgo 'All-In'."""
    portafolio_id = portafolio.get("id")
    holdings = portafolio.get("holdings", [])
    cash_after_tx = portafolio.get("cash", 0)
    tx_type = transaction.get("type")
    
    # --- 1. Lógica 'All-In' (Gastar todo el efectivo) ---
    if tx_type == "BUY":
        tx_cost = transaction.get("amount", 0) * transaction.get("price", 0)
        cash_before_tx = cash_after_tx + tx_cost
        
        if cash_before_tx > 0 and (tx_cost / cash_before_tx) > 0.50:
            msg = (f"¡Alerta de Riesgo! Usaste el { (tx_cost / cash_before_tx) * 100:.0f}% de tu "
                   f"efectivo disponible en una sola compra de {transaction.get('activeSymbol')}. "
                   "Evita ir 'All-In' para gestionar mejor el riesgo.")
            send_feedback_to_nestjs(portafolio_id, msg, "RISK_ALERT")
            
    # --- 2. Revisar concentración ---
    
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
            total_value += value 
            
    if total_value == 0:
        return 

    for symbol, value in asset_values.items():
        concentration = (value / total_value) * 100
        if concentration > 30: 
            msg = f"¡Alerta de Riesgo! Tienes un {concentration:.0f}% de tu portafolio en {symbol}. Considera diversificar."
            send_feedback_to_nestjs(portafolio_id, msg, "RISK_ALERT")
    pass

def _analyze_costs_and_slippage(transaction: dict, market_data: dict):
    """HU9: Analiza costos (comisión simulada) y slippage."""
    portafolio_id = transaction.get("portafolioId")
    symbol = transaction.get("activeSymbol")
    tx_type = transaction.get("type")
    tx_price = transaction.get("price", 0)
    tx_amount = transaction.get("amount", 0)

    # --- 1. Análisis de Comisión (Simulada) ---
    total_cost_usd = tx_amount * tx_price
    commission_paid = total_cost_usd * SIMULATED_FEE_RATE
    
    msg_cost = (f"Análisis de Costos: Tu transacción de {symbol} generó "
                f"una comisión simulada de ${commission_paid:.2f} (0.5%).")
    send_feedback_to_nestjs(portafolio_id, msg_cost, "COST_ANALYSIS")

    # --- 2. Análisis de Slippage (Deslizamiento) ---
    if symbol not in market_data:
        return 

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
    pass

def _analyze_behavior(transaction: dict, market_data: dict):
    """HU7: Analiza sesgos conductuales (FOMO y Venta de Pánico)."""
    portafolio_id = transaction.get("portafolioId")
    symbol = transaction.get("activeSymbol")
    tx_type = transaction.get("type")
    
    if symbol not in market_data:
        return 

    ticker = market_data[symbol]
    price_change_24h = float(ticker.get("price_percent_chg_24_h", 0))

    # --- 1. Lógica de FOMO (Comprar alto) ---
    if tx_type == "BUY":
        if price_change_24h > 0:
            msg_fomo = (f"Análisis Conductual: Compraste {symbol} después de que subió un "
                        f"{price_change_24h:.2f}% en 24 horas. ¿Podría ser FOMO (Miedo a Quedarse Fuera)?")
            send_feedback_to_nestjs(portafolio_id, msg_fomo, "BEHAVIORAL_NUDGE")

    # --- 2 LÓGICA: Venta de Pánico (Vender bajo) ---
    elif tx_type == "SELL":
        if price_change_24h < 0:
            msg_panic = (f"Análisis Conductual: Vendiste {symbol} después de que cayó un "
                         f"{price_change_24h:.2f}% en 24 horas. ¿Estás seguro de que no es "
                         "una Venta de Pánico?")
            send_feedback_to_nestjs(portafolio_id, msg_panic, "BEHAVIORAL_NUDGE")
    pass