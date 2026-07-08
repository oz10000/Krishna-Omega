#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse
import config
from telemetry import log_info, log_error, log_success

def main():
    parser = argparse.ArgumentParser(description='Krishna Omega Ultra')
    parser.add_argument('--mode', choices=['backtest', 'optimize', 'demo', 'live'],
                        default='demo', help='Modo de ejecución')
    args = parser.parse_args()

    # Verificar modo LIVE (bloqueado por defecto)
    if args.mode == 'live' and not getattr(config, 'ENABLE_LIVE', False):
        log_error("Main", "MODO LIVE DESACTIVADO. Configure ENABLE_LIVE=true en config para habilitar.")
        sys.exit(1)

    log_info("Main", f"Iniciando KRISHNA OMEGA ULTRA en modo {args.mode}")

    if args.mode == 'backtest':
        from modes.backtest_mode import main as backtest_main
        backtest_main()
    elif args.mode == 'optimize':
        from modes.optimization_mode import main as optimize_main
        optimize_main()
    elif args.mode == 'demo':
        from modes.demo_mode import main as demo_main
        demo_main()
    elif args.mode == 'live':
        from modes.live_mode import main as live_main
        live_main()
    else:
        log_error("Main", f"Modo desconocido: {args.mode}")
        sys.exit(1)

if __name__ == "__main__":
    main()
