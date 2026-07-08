#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Signal:
    symbol: str
    direction: str
    timestamp: datetime
    entry: float
    tp: float
    sl: float
    raw_score: float
    roc_5m: float
    speed_score: float


@dataclass
class Position:
    symbol: str
    side: str
    size: float
    entry_price: float
    mark_price: float
    pnl: float
    pnl_pct: float


@dataclass
class OrderResult:
    ord_id: str
    algo_id: Optional[str] = None
    avg_px: Optional[float] = None
    state: Optional[str] = None


@dataclass
class Balance:
    total: float
    free: float
    frozen: float


@dataclass
class ProtectionStatus:
    tp_exists: bool
    sl_exists: bool
    trail_exists: bool


@dataclass
class MarketData:
    symbol: str
    price: float
    atr: float
    ker: float
    zscore: float
    roc: float
    volume_ratio: float
