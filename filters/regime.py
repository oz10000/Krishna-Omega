
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import config
from strategy.pidelta_strategy import compute_adx, compute_atr

def calculate_ker(close: pd.Series, period: int) -> float:
    abs_diff = abs(close.diff(period).iloc[-1])
    sum_abs = close.diff().abs().rolling(period).sum().iloc[-1]
    return abs_diff / (sum_abs + 1e-9)

def is_regime_valid(df: pd.DataFrame, symbol: str) -> dict:
    adx = compute_adx(df, config.ADX_PERIOD).iloc[-1]
    ker = calculate_ker(df['c'], config.KER_PERIOD)
    atr_pct = compute_atr(df, config.ATR_PERIOD).iloc[-1] / df.iloc[-1]['c'] * 100
    if adx < config.ADX_THRESHOLD:
        return {'valid': False, 'reason': f'ADX {adx:.1f} < {config.ADX_THRESHOLD}'}
    if ker < config.KER_THRESHOLD:
        return {'valid': False, 'reason': f'KER {ker:.2f} < {config.KER_THRESHOLD}'}
    if atr_pct < config.ATR_MIN_PCT:
        return {'valid': False, 'reason': f'ATR% {atr_pct:.2f} < {config.ATR_MIN_PCT}'}
    if atr_pct > config.ATR_MAX_PCT:
        return {'valid': False, 'reason': f'ATR% {atr_pct:.2f} > {config.ATR_MAX_PCT}'}
    return {'valid': True, 'reason': 'OK'}
