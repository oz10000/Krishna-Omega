
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pandas as pd
import config
from backtesting.engine import run_backtest
from telemetry import log_info, log_error, log_success

def load_data(data_dir: str = config.DATA_DIR) -> dict:
    data = {}
    if not os.path.exists(data_dir):
        log_error("Backtest", f"Directorio {data_dir} no existe")
        return data
    for file in os.listdir(data_dir):
        if file.endswith('.csv'):
            symbol = file.split('_')[0]
            try:
                df = pd.read_csv(os.path.join(data_dir, file), parse_dates=['ts'])
                df = df.sort_values('ts').reset_index(drop=True)
                data[symbol] = df
                log_info("Backtest", f"Cargado {symbol}: {len(df)} velas")
            except Exception as e:
                log_error("Backtest", f"Error cargando {file}: {e}")
    return data

def main():
    log_info("Backtest", "Iniciando modo BACKTEST")
    data = load_data()
    if not data:
        log_error("Backtest", "No se cargaron datos")
        return
    result = run_backtest(data, config.CAPITAL_INICIAL)
    metrics = result['metrics']
    print("\n" + "="*60)
    print("RESULTADOS BACKTEST")
    print("="*60)
    for k, v in metrics.items():
        print(f"{k:25}: {v}")
    print(f"Trades totales      : {len(result['trades'])}")
    print("="*60)
    pd.DataFrame(result['trades']).to_csv("backtest_trades.csv", index=False)
    log_success("Backtest", "Resultados guardados en backtest_trades.csv")

if __name__ == "__main__":
    main()
