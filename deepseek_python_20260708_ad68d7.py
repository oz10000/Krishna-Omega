#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

# ---------- ACTIVOS Y CAPITAL ----------
SYMBOLS = ['BTC', 'ETH', 'SOL', 'ADA', 'XRP', 'AVAX']
CAPITAL_INICIAL = 1000.0
TRADE_NOTIONAL = 100.0
LEVERAGE = 10

# ---------- PARÁMETROS PiDelta ----------
KER_PERIOD = 10
VWAP_PERIOD = 20
ATR_PERIOD = 14
EMA_FAST = 20
SLOPE_PERIOD = 5
MACRO_LOOKBACK = 20
MOMENTUM_PERIOD = 5
ADX_PERIOD = 14

PIDELTA_WEIGHTS = {
    'trend': 0.30,
    'regime': 0.25,
    'macro': 0.20,
    'strength': 0.15,
    'momentum': 0.10
}

# ---------- UMBRALES Y SALIDAS ----------
MIN_SCORE = 0.40
TP_MULT = 1.8
SL_MULT = 0.9
COOLDOWN_SECONDS = 15 * 60
BREAK_EVEN_MINUTES = 15
MAX_HOLD_MINUTES = 60
BREAK_EVEN_BUFFER = 0.10

# ---------- PARÁMETROS POR ACTIVO ----------
ACTIVE_CONFIG = {
    'BTC': {'tp_mult': 2.8, 'sl_mult': 0.8, 'min_score': 0.35, 'be_min': 18, 'trail_callback': 0.005},
    'ETH': {'tp_mult': 2.4, 'sl_mult': 0.9, 'min_score': 0.38, 'be_min': 15, 'trail_callback': 0.006},
    'SOL': {'tp_mult': 3.0, 'sl_mult': 0.7, 'min_score': 0.32, 'be_min': 20, 'trail_callback': 0.004},
    'ADA': {'tp_mult': 2.0, 'sl_mult': 1.0, 'min_score': 0.42, 'be_min': 12, 'trail_callback': 0.007},
    'XRP': {'tp_mult': 2.2, 'sl_mult': 0.9, 'min_score': 0.40, 'be_min': 15, 'trail_callback': 0.005},
    'AVAX': {'tp_mult': 2.0, 'sl_mult': 1.1, 'min_score': 0.45, 'be_min': 10, 'trail_callback': 0.008},
}

# ---------- FILTROS ----------
VALID_HOURS = [14, 15, 16, 17, 21, 22, 23, 0]  # UTC
ADX_THRESHOLD = 22
KER_THRESHOLD = 0.50
ATR_MIN_PCT = 0.4
ATR_MAX_PCT = 2.5
CORRELATION_THRESHOLD = 0.70
MAX_POSITIONS = 2

# ---------- SIZING ----------
KELLY_FRACTION = 0.5
VOLATILITY_TARGET = 0.015  # 1.5%

# ---------- DIRECTORIOS ----------
METRICS_DIR = "metrics"
LOGS_DIR = "logs"
SNAPSHOTS_DIR = "snapshots"
DATA_DIR = "data/candles_5m"

# ---------- MODO LIVE ----------
ENABLE_LIVE = False  # BLOQUEADO POR DEFECTO

# ---------- MODO DE EJECUCIÓN ----------
MODE = os.environ.get('KRISHNA_MODE', 'demo')