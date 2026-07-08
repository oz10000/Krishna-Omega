
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional
import config
from telemetry import log_info, log_warning

class TrailingManager:
    def __init__(self, exchange, symbol: str, side: str, size: float,
                 callback_base: Optional[float] = None):
        self.exchange = exchange
        self.symbol = symbol
        self.side = side
        self.size = size
        self.callback = callback_base or self._get_default_callback(symbol)
        self.active = False
        self.algo_id = None

    def _get_default_callback(self, symbol: str) -> float:
        return config.ACTIVE_CONFIG.get(symbol, {}).get('trail_callback', 0.005)

    def activate(self, current_price: float) -> bool:
        if self.active:
            return True
        side = 'sell' if self.side == 'long' else 'buy'
        result = self.exchange.place_trailing_stop_order(
            self.symbol, side, self.size, self.callback
        )
        if result.get('ok'):
            self.algo_id = result['data'].algo_id
            self.active = True
            log_info("TrailingManager", f"Trailing activado para {self.symbol}",
                     {"callback": self.callback, "algo_id": self.algo_id})
            return True
        else:
            log_warning("TrailingManager", f"Fallo al activar trailing para {self.symbol}",
                        {"error": result.get('error')})
            return False

    def deactivate(self) -> bool:
        if not self.active or not self.algo_id:
            return True
        result = self.exchange.cancel_algo_order(self.symbol, self.algo_id)
        if result.get('ok'):
            self.active = False
            self.algo_id = None
            log_info("TrailingManager", f"Trailing desactivado para {self.symbol}")
            return True
        return False

    def adjust_callback(self, new_callback: float) -> bool:
        if not self.active:
            self.callback = new_callback
            return True
        if self.deactivate():
            self.callback = new_callback
            return self.activate(0)
        return False
