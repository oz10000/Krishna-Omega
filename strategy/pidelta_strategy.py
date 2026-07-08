#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from typing import Optional, Dict, List
import config
from telemetry import log_debug

# ---------- INDICADORES ----------
def compute_ker(close: pd.Series, period: int) -> pd.Series:
    abs_diff = abs(close.diff(period))
    sum_abs = close.diff().abs().rolling(period).sum()
    return abs_diff / (sum_abs + 1e-9)

def compute_vwap_zscore(df: pd.DataFrame, period: int) -> pd.Series:
    vwap = (df['c'] * df['vol']).rolling(period).sum() / (df['vol'].rolling(period).sum() + 1e-9)
    std = df['c'].rolling(period).std()
    return (df['c'] - vwap) / (std + 1e-9)

def compute_atr(df: pd.DataFrame, period: int) -> pd.Series:
    tr = pd.concat([
        df['h'] - df['l'],
        abs(df['h'] - df['c'].shift()),
        abs(df['l'] - df['c'].shift())
    ], axis=1).max(axis=1)
    return tr.rolling(period).mean()

def compute_ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()

def compute_adx(df: pd.DataFrame, period: int) -> pd.Series:
    atr = compute_atr(df, period)
    up_move = df['h'].diff()
    down_move = -df['l'].diff()
    plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0)
    minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0)
    plus_di = 100 * (plus_dm.rolling(period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(period).mean() / atr)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
    return dx.rolling(period).mean()

def compute_macro(df: pd.DataFrame, period: int) -> pd.Series:
    atr = compute_atr(df, config.ATR_PERIOD)
    macro = atr.rolling(period).apply(
        lambda x: (x.iloc[-1] - x.min()) / (x.max() - x.min() + 1e-9)
    )
    return macro.clip(0, 1)

# ---------- PiDelta Score ----------
def compute_pidelta_score(df: pd.DataFrame) -> float:
    if len(df) < 50:
        return 0.0
    
    ker = compute_ker(df['c'], config.KER_PERIOD)
    vwap_z = compute_vwap_zscore(df, config.VWAP_PERIOD)
    atr = compute_atr(df, config.ATR_PERIOD)
    ema = compute_ema(df['c'], config.EMA_FAST)
    slope = (df['c'] - ema) / (atr + 1e-9)
    adx = compute_adx(df, config.ADX_PERIOD)
    momentum = df['c'].pct_change(config.MOMENTUM_PERIOD) * 100
    macro = compute_macro(df, config.MACRO_LOOKBACK)

    # Últimos valores con checks de NaN
    ker_l = ker.iloc[-1] if not ker.isna().all() else 0.5
    vwz_l = vwap_z.iloc[-1] if not vwap_z.isna().all() else 0.0
    slope_l = slope.iloc[-1] if not slope.isna().all() else 0.0
    adx_l = adx.iloc[-1] if not adx.isna().all() else 20.0
    mom_l = momentum.iloc[-1] if not momentum.isna().all() else 0.0
    macro_l = macro.iloc[-1] if not macro.isna().all() else 0.5

    trend = np.tanh(slope_l)  # -1 a 1
    regime = ker_l  # 0 a 1
    macro_score = macro_l  # 0 a 1
    strength = min(1.0, adx_l / 40.0)
    mom_score = min(1.0, abs(mom_l) / 5.0)

    raw = (config.PIDELTA_WEIGHTS.get('trend', 0.30) * trend +
           config.PIDELTA_WEIGHTS.get('regime', 0.25) * regime +
           config.PIDELTA_WEIGHTS.get('macro', 0.20) * macro_score +
           config.PIDELTA_WEIGHTS.get('strength', 0.15) * strength +
           config.PIDELTA_WEIGHTS.get('momentum', 0.10) * mom_score)
    return float(np.tanh(raw))

# ---------- Interfaz para main.py ----------
def get_best_signal(symbols: List[str], df_dict: Dict[str, pd.DataFrame]) -> Optional[Dict]:
    best_score = -999
    best_signal = None
    for symbol in symbols:
        if symbol not in df_dict:
            continue
        df = df_dict[symbol]
        if len(df) < 60:
            continue
        score = compute_pidelta_score(df)
        if abs(score) < config.MIN_SCORE:
            continue
        cfg = config.ACTIVE_CONFIG.get(symbol, {})
        tp_mult = cfg.get('tp_mult', config.TP_MULT)
        sl_mult = cfg.get('sl_mult', config.SL_MULT)
        entry = df.iloc[-1]['c']
        atr = compute_atr(df, config.ATR_PERIOD).iloc[-1]
        adx = compute_adx(df, config.ADX_PERIOD).iloc[-1]
        direction = 'Long' if score > 0 else 'Short'
        if direction == 'Long':
            tp = entry + atr * tp_mult
            sl = entry - atr * sl_mult
        else:
            tp = entry - atr * tp_mult
            sl = entry + atr * sl_mult
        if abs(score) > best_score:
            best_score = abs(score)
            best_signal = {
                'symbol': symbol,
                'direction': direction,
                'entry': entry,
                'tp': tp,
                'sl': sl,
                'score': score,
                'raw_score': score,
                'atr': atr,
                'adx': adx if not np.isnan(adx) else 0.0,
                'ker': ker.iloc[-1] if not ker.isna().all() else 0.5
            }
    return best_signal
