
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import config
from exchange.okx_exchange import OKXExchange
from telemetry import log_info, log_error, log_success

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
        log_error("Demo", "Conexion fallida")
        return
    log_success("Demo", "Conexion OKX establecida")

    bal = exchange.get_balance()
    if bal.get('ok'):
        log_success("Demo", f"Balance: {bal['data'].total:.2f} USDT")
    else:
        log_error("Demo", "Error obteniendo balance")

    pos = exchange.get_positions()
    if pos.get('ok'):
        log_success("Demo", f"Posiciones activas: {len(pos['data'])}")
    else:
        log_error("Demo", "Error obteniendo posiciones")

    test_symbol = 'BTC-USDT-SWAP'
    test_size = 0.001
    order = exchange.place_market_order(test_symbol, 'buy', test_size, leverage=1)
    if order.get('ok'):
        log_success("Demo", f"Orden market creada: {order['data'].ord_id}")
        time.sleep(2)
        cancel = exchange.cancel_order(test_symbol, order['data'].ord_id)
        if cancel.get('ok'):
            log_success("Demo", "Orden cancelada")
        else:
            log_error("Demo", "Fallo al cancelar")
    else:
        log_error("Demo", f"Error creando orden: {order.get('error')}")

    log_success("Demo", "DEMO MODE COMPLETADO")

if __name__ == "__main__":
    main()
