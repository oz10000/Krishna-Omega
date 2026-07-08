#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import time
from typing import Dict
import config

class RiskController:
    def __init__(self, capital_inicial: float = None):
        self.capital_inicial = capital_inicial or config.CAPITAL_INICIAL
        self.equity_peak = self.capital_inicial
        self.equity_current = self.capital_inicial
        self.dd_actual = 0.0
        self.dd_max_historico = 0.0
        self.mode = "NORMAL"
        self.kill_switch_activated = False
        self.kill_reason = ""
        self._history = []
        self._last_update = time.time()
        os.makedirs(config.SNAPSHOTS_DIR, exist_ok=True)

    def update(self, equity_current: float) -> Dict:
        self.equity_current = equity_current
        if equity_current > self.equity_peak:
            self.equity_peak = equity_current
        if self.equity_peak > 0:
            self.dd_actual = ((self.equity_peak - self.equity_current) / self.equity_peak) * 100
        else:
            self.dd_actual = 0.0
        self.dd_actual = max(0.0, self.dd_actual)
        if self.dd_actual > self.dd_max_historico:
            self.dd_max_historico = self.dd_actual
        self._history.append(self.dd_actual)
        if len(self._history) > 100:
            self._history.pop(0)
        self._determine_mode()
        if config.KILL_SWITCH_ENABLED and self.dd_actual >= config.KILL_THRESHOLD:
            self._activate_kill_switch(f"Drawdown {self.dd_actual:.2f}% ≥ {config.KILL_THRESHOLD}%")
        return self.get_metrics()

    def _determine_mode(self):
        if self.kill_switch_activated:
            self.mode = "KILL"
            return
        if self.dd_actual < config.DD_NORMAL_LIMIT:
            self.mode = "NORMAL"
        elif self.dd_actual < config.DD_REDUCED_LIMIT:
            self.mode = "REDUCIDO"
        else:
            self.mode = "PROTECCIÓN"

    def _activate_kill_switch(self, reason: str):
        if self.kill_switch_activated:
            return
        self.kill_switch_activated = True
        self.kill_reason = reason
        self.mode = "KILL"

    def is_kill_switch_activated(self) -> bool:
        return self.kill_switch_activated

    def get_effective_parameters(self) -> Dict:
        if self.mode == "NORMAL":
            return {'leverage': config.LEVERAGE_NORMAL, 'size_factor': config.SIZE_FACTOR_NORMAL,
                    'mode': 'NORMAL', 'trading_enabled': True, 'min_score_boost': 0.0}
        elif self.mode == "REDUCIDO":
            return {'leverage': config.LEVERAGE_REDUCED, 'size_factor': config.SIZE_FACTOR_REDUCED,
                    'mode': 'REDUCIDO', 'trading_enabled': True, 'min_score_boost': 0.05}
        elif self.mode == "PROTECCIÓN":
            return {'leverage': config.LEVERAGE_PROTECTION, 'size_factor': config.SIZE_FACTOR_PROTECTION,
                    'mode': 'PROTECCIÓN', 'trading_enabled': True, 'min_score_boost': 0.15}
        else:
            return {'leverage': 0, 'size_factor': 0.0, 'mode': 'KILL',
                    'trading_enabled': False, 'min_score_boost': 1.0}

    def get_volatility_targeted_size(self, base_size: float, atr_pct: float) -> float:
        target = config.VOLATILITY_TARGET * 100
        if atr_pct == 0:
            return base_size
        size = base_size * (target / atr_pct)
        return max(base_size * 0.2, min(base_size * 2.0, size))

    def get_kelly_fraction(self, win_rate: float, avg_win: float, avg_loss: float) -> float:
        if avg_loss == 0:
            return 0.0
        b = avg_win / avg_loss
        if b <= 0:
            return 0.0
        f = (b * win_rate - (1 - win_rate)) / b
        f = max(0.0, min(0.25, f))
        return f * config.KELLY_FRACTION

    def get_metrics(self) -> Dict:
        params = self.get_effective_parameters()
        return {
            'dd_actual': round(self.dd_actual, 2),
            'dd_max_historico': round(self.dd_max_historico, 2),
            'mode': self.mode,
            'leverage_effective': params['leverage'],
            'size_factor': round(params['size_factor'], 3),
            'trading_enabled': params['trading_enabled'],
            'kill_switch_activated': self.kill_switch_activated,
            'kill_reason': self.kill_reason,
        }
