
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional
import config

class BreakEvenEngine:
    def __init__(self, symbol: str, entry_price: float, side: str):
        self.symbol = symbol
        self.entry_price = entry_price
        self.side = side
        self.be_activated = False
        self.be_price = None
        self._elapsed = 0

    def update(self, elapsed_minutes: float, current_price: float, pnl_pct: float,
               adx: Optional[float] = None) -> bool:
        if self.be_activated:
            return False
        cfg = config.ACTIVE_CONFIG.get(self.symbol, {})
        min_be_time = cfg.get('be_min', config.BREAK_EVEN_MINUTES)
        min_profit_pct = 0.5
        if elapsed_minutes < min_be_time:
            return False
        if pnl_pct < min_profit_pct:
            return False
        if adx is not None and adx > 25 and elapsed_minutes < 20:
            return False
        self.be_activated = True
        buffer = config.BREAK_EVEN_BUFFER / 100
        if self.side == 'long':
            self.be_price = self.entry_price * (1 + buffer)
        else:
            self.be_price = self.entry_price * (1 - buffer)
        return True

    def get_be_price(self) -> Optional[float]:
        return self.be_price if self.be_activated else None
