#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional
from models import Position
from position.trailing import TrailingManager
from position.break_even import BreakEvenEngine
from telemetry import log_info, log_warning

class PositionManager:
    def __init__(self, exchange, position: Position, config_module):
        self.exchange = exchange
        self.position = position
        self.config = config_module
        self.trailing = None
        self.be_engine = BreakEvenEngine(position.symbol, position.entry_price, position.side)
        self._tp_placed = False
        self._sl_placed = False
        self._trailing_activated = False

    def setup_initial_protections(self, tp_price: float, sl_price: float) -> bool:
        side = 'sell' if self.position.side == 'long' else 'buy'
        result = self.exchange.place_algo_order(
            self.position.symbol, side, self.position.size,
            tp_price=tp_price, sl_price=sl_price
        )
        if result.get('ok'):
            self._tp_placed = True
            self._sl_placed = True
            log_info("PositionManager", "TP/SL iniciales colocados")
            return True
        else:
            log_warning("PositionManager", "Fallo al colocar TP/SL iniciales")
            return False

    def update(self, current_price: float, pnl_pct: float, elapsed_minutes: float,
               adx: Optional[float] = None) -> dict:
        # 1. Break Even
        be_activated = self.be_engine.update(elapsed_minutes, current_price, pnl_pct, adx)
        if be_activated:
            be_price = self.be_engine.get_be_price()
            if be_price:
                log_info("PositionManager", f"Break Even activado a {be_price:.2f}")
                return {'action': 'modify_sl', 'price': be_price}

        # 2. Timeout
        if elapsed_minutes >= self.config.MAX_HOLD_MINUTES:
            log_info("PositionManager", f"Timeout: {elapsed_minutes:.1f} min")
            return {'action': 'close', 'reason': 'Timeout'}

        # 3. Trailing (si PnL > 2%)
        if pnl_pct > 2.0 and not self._trailing_activated:
            self.activate_trailing()
            return {'action': 'activate_trailing', 'callback': self.get_trailing_callback()}

        return {'action': 'hold'}

    def activate_trailing(self) -> bool:
        if self._trailing_activated:
            return True
        side = 'sell' if self.position.side == 'long' else 'buy'
        cfg = self.config.ACTIVE_CONFIG.get(self.position.symbol, {})
        callback = cfg.get('trail_callback', 0.005)
        result = self.exchange.place_trailing_stop_order(
            self.position.symbol, side, self.position.size, callback
        )
        if result.get('ok'):
            self._trailing_activated = True
            log_info("PositionManager", f"Trailing activado con callback {callback}")
            return True
        return False

    def get_trailing_callback(self) -> float:
        cfg = self.config.ACTIVE_CONFIG.get(self.position.symbol, {})
        return cfg.get('trail_callback', 0.005)
