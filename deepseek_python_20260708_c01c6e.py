#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import config
from strategy.pidelta_strategy import get_best_signal
from backtesting.simulator import simulate_trade
from backtesting.metrics import calculate_metrics
from telemetry import log_info, log_debug

def run_backtest(data: dict, capital: float, commission: float = 0.0004, slippage: float = 0.0005) -> dict:
    trades = []
    equity = capital
    cooldown = {}
    cooldown_velas = config.COOLDOWN_SECONDS // 300  # 5m velas

    for symbol, df in data.items():
        if df.empty:
            continue
        log_info("Backtest", f"Procesando {symbol} ({len(df)} velas)")
        for i in range(60, len(df) - 1):  # -1 para evitar índice fuera de rango
            # 1. Calcular indicadores en vela i (cerrada)
            current_df = df.iloc[:i+1].copy()
            signal = get_best_signal([symbol], {symbol: current_df})
            if signal is None:
                continue
            # 2. Verificar cooldown
            if symbol in cooldown:
                if (i - cooldown[symbol]) < cooldown_velas:
                    continue
            # 3. Ejecutar entrada en vela i+1 (siguiente vela)
            entry_price = df.iloc[i+1]['c']
            entry_time = df.iloc[i+1]['ts']
            trade = simulate_trade(
                signal=signal,
                df=df,
                entry_idx=i+1,
                entry_price=entry_price,
                entry_time=entry_time,
                commission=commission,
                slippage=slippage,
                trade_notional=config.TRADE_NOTIONAL
            )
            if trade:
                trades.append(trade)
                equity += trade['pnl_usdt']
                cooldown[symbol] = i
                log_debug("Backtest", f"Trade {symbol} {trade['direction']}: {trade['pnl_usdt']:.2f} USDT")

    metrics = calculate_metrics(trades, capital, equity)
    return {'trades': trades, 'metrics': metrics, 'final_equity': equity}