#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import config

def simulate_trade(signal, df, entry_idx, entry_price, entry_time,
                   commission=0.0004, slippage=0.0005, trade_notional=100.0):
    direction = signal['direction']
    tp_raw = signal['tp']
    sl_raw = signal['sl']
    size = trade_notional / entry_price

    # Aplicar slippage a entrada
    if direction == 'Long':
        entry_price_adj = entry_price * (1 + slippage)
    else:
        entry_price_adj = entry_price * (1 - slippage)

    max_hold_velas = config.MAX_HOLD_MINUTES // 5
    be_min_velas = config.BREAK_EVEN_MINUTES // 5
    be_buffer = config.BREAK_EVEN_BUFFER / 100

    result = 'Timeout'
    exit_price = entry_price_adj
    exit_time = entry_time

    for j in range(entry_idx + 1, min(entry_idx + max_hold_velas + 1, len(df))):
        close = df.iloc[j]['c']
        high = df.iloc[j]['h']
        low = df.iloc[j]['l']
        elapsed_velas = j - entry_idx
        elapsed_minutes = elapsed_velas * 5

        # Aplicar slippage a TP/SL
        if direction == 'Long':
            tp_eff = tp_raw * (1 - slippage)
            sl_eff = sl_raw * (1 + slippage)
            if high >= tp_eff:
                exit_price = tp_eff
                result = 'TP'
                break
            if low <= sl_eff:
                exit_price = sl_eff
                result = 'SL'
                break
        else:
            tp_eff = tp_raw * (1 + slippage)
            sl_eff = sl_raw * (1 - slippage)
            if low <= tp_eff:
                exit_price = tp_eff
                result = 'TP'
                break
            if high >= sl_eff:
                exit_price = sl_eff
                result = 'SL'
                break

        # Break Even
        if elapsed_minutes >= config.BREAK_EVEN_MINUTES:
            pnl_pct = (close - entry_price_adj) / entry_price_adj * 100 if direction == 'Long' else (entry_price_adj - close) / entry_price_adj * 100
            if pnl_pct > be_buffer:
                if direction == 'Long':
                    exit_price = entry_price_adj * (1 + be_buffer)
                else:
                    exit_price = entry_price_adj * (1 - be_buffer)
                result = 'BE'
                break

        exit_time = df.iloc[j]['ts']

    # Comisiones
    pnl_usdt = (exit_price - entry_price_adj) * size if direction == 'Long' else (entry_price_adj - exit_price) * size
    pnl_usdt -= pnl_usdt * commission * 2

    return {
        'symbol': signal['symbol'],
        'direction': direction,
        'entry': entry_price_adj,
        'exit': exit_price,
        'pnl_usdt': pnl_usdt,
        'result': result,
        'timestamp': entry_time,
        'exit_time': exit_time,
        'duration_min': (exit_time - entry_time).total_seconds() / 60,
        'score': signal['score'],
        'adx': signal.get('adx', 0),
        'ker': signal.get('ker', 0)
    }
