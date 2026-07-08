
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import config
from exchange.okx_exchange import OKXExchange
from telemetry import log_info, log_error, log_critical, log_success

def main():
    log_critical("Live", "MODO LIVE ACTIVADO - TRADING REAL")
    if not config.ENABLE_LIVE:
        log_error("Live", "ENABLE_LIVE esta desactivado en config.py")
        return

    api_key = os.environ.get('OKX_API_KEY')
    secret = os.environ.get('OKX_SECRET_KEY')
    passphrase = os.environ.get('OKX_PASSPHRASE')
    if not all([api_key, secret, passphrase]):
        log_error("Live", "Faltan credenciales")
        return

    exchange = OKXExchange(api_key, secret, passphrase, demo=False)
    if not exchange.connect():
        log_error("Live", "Conexion fallida")
        return
    log_success("Live", "Conexion OKX establecida (LIVE)")

    log_info("Live", "Sistema listo para operar en LIVE")

if __name__ == "__main__":
    main()
