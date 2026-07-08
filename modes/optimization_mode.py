
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import pandas as pd
from itertools import product
import config
from backtesting.engine import run_backtest
from telemetry import log_info, log_error, log_success

def grid_search(param_grid, data, capital):
    results = []
    keys = list(param_grid.keys())
    values = list(param_grid.values())
    for combination in product(*values):
        params = dict(zip(keys, combination))
        original = {}
        for k, v in params.items():
            if hasattr(config, k):
                original[k] = getattr(config, k)
                setattr(config, k, v)
        result = run_backtest(data, capital)
        result['params'] = params
        results.append(result)
        for k, v in original.items():
            setattr(config, k, v)
        log_info("Optimization", f"Combinacion {len(results)}: PF {result['metrics'].get('Profit Factor', 0):.2f}")
    return results

def main():
    log_info("Optimization", "Iniciando modo OPTIMIZE")
    from modes.backtest_mode import load_data
    data = load_data()
    if not data:
        log_error("Optimization", "No se cargaron datos")
        return
    param_grid = {
        'TP_MULT': [1.5, 2.0, 2.5, 3.0],
        'SL_MULT': [0.6, 0.8, 1.0, 1.2],
        'MIN_SCORE': [0.30, 0.35, 0.40, 0.45],
        'ADX_THRESHOLD': [20, 22, 25],
    }
    results = grid_search(param_grid, data, config.CAPITAL_INICIAL)
    if results:
        best = max(results, key=lambda x: x['metrics'].get('Profit Factor', 0))
        log_success("Optimization", f"Mejor PF: {best['metrics'].get('Profit Factor', 0):.2f}")
        log_info("Optimization", f"Parametros: {best['params']}")
        os.makedirs("optimization_results", exist_ok=True)
        with open("optimization_results/best_parameters.json", "w") as f:
            json.dump(best['params'], f, indent=2)
        pd.DataFrame([r['params'] for r in results]).to_csv("optimization_results/optimization_report.csv", index=False)
        log_success("Optimization", "Resultados guardados en optimization_results/")
    else:
        log_error("Optimization", "No se encontraron resultados")

if __name__ == "__main__":
    main()
