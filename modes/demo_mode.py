#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import config
from exchange.okx_exchange import OKXExchange
from position.position_manager import PositionManager
from models import Position
from telemetry import log_info, log_success, log_error

def main():
    log_info("Demo", "Iniciando modo DEMO")
    api_key = os.environ.get('OKX_API_KEY')
    secret = os.environ.get('OKX_SECRET_KEY')
    passphrase = os.environ.get('OKX_PASSPHRASE')
    if not all([api_key, secret, passphrase]):
        log_error("Demo", "Faltan credenciales")
        return

    exchange = OKXExchange(api_key, secret, passphrase, demo=True)
    if not exchange.connect():
        log_error("Demo", "Conexión fallida")
        return
    log_success("Demo", "Conexión OKX establecida")

    # Balance
    bal = exchange.get_balance()
    if bal.get('ok'):
        log_success("Demo", f"Balance: {bal['data'].total:.2f} USDT")
    else:
        log_error("Demo", "Error obteniendo balance")

    # Posiciones
    pos = exchange.get_positions()
    if pos.get('ok'):
        log_success("Demo", f"Posiciones activas: {len(pos['data'])}")
        for p in pos['data']:
            log_info("Demo", f"  {p.symbol} {p.side} size={p.size} PnL={p.pnl:.2f}")
    else:
        log_error("Demo", "Error obteniendo posiciones")

    # Crear orden de prueba (solo si no hay posiciones)
    if not pos.get('data'):
        symbol = 'BTC-USDT-SWAP'
        size = 0.001
        order = exchange.place_market_order(symbol, 'buy', size, leverage=1)
        if order.get('ok'):
            log_success("Demo", f"Orden market creada: {order['data'].ord_id}")
            time.sleep(2)
            # Cancelar
            cancel = exchange.cancel_order(symbol, order['data'].ord_id)
            if cancel.get('ok'):
                log_success("Demo", "Orden cancelada")
            else:
                log_error("Demo", "Fallo al cancelar")
        else:
            log_error("Demo", f"Error creando orden: {order.get('error')}")

    log_success("Demo", "✅ DEMO MODE COMPLETADO")
