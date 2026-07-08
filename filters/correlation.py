
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from typing import Dict, List
import config

class CorrelationManager:
    def __init__(self, data: Dict[str, pd.DataFrame], lookback: int = 50):
        self.data = data
        self.lookback = lookback
        self._cache = {}

    def get_correlation(self, sym1: str, sym2: str) -> float:
        key = f"{sym1}:{sym2}"
        if key in self._cache:
            return self._cache[key]
        if sym1 not in self.data or sym2 not in self.data:
            return 0.0
        df1 = self.data[sym1]['c'].iloc[-self.lookback:]
        df2 = self.data[sym2]['c'].iloc[-self.lookback:]
        corr = df1.corr(df2)
        if np.isnan(corr):
            corr = 0.0
        self._cache[key] = corr
        return corr

    def can_open(self, symbol: str, open_positions: List[str], threshold: float = None) -> bool:
        if threshold is None:
            threshold = config.CORRELATION_THRESHOLD
        for pos in open_positions:
            if pos == symbol:
                continue
            if self.get_correlation(symbol, pos) > threshold:
                return False
        return True
