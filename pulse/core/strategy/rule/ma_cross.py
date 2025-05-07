from __future__ import annotations
from collections import deque
from typing import Dict, Any

import pandas as pd

from pulse.core.strategy.base_strategy import BaseStrategy
from pulse.core.execution.trade_models import Order
from core.order_management.sequence import next_seq


class MaCrossStrategy(BaseStrategy):
    """均线交叉示例"""

    def __init__(self, name: str, params: Dict[str, Any]):
        super().__init__(name, params)
        self.short_window = int(params.get("short_window", 5))
        self.long_window  = int(params.get("long_window", 20))
        if self.short_window >= self.long_window:
            raise ValueError("short_window 必须 < long_window")

        self.short_prices = deque(maxlen=self.short_window)
        self.long_prices  = deque(maxlen=self.long_window)
        self.in_position  = False
        self.qty          = int(params.get("qty", 10))

    def on_bar(self, bar: pd.Series) -> None:
        close = float(bar["close"])
        dt    = bar.name
        self.short_prices.append(close)
        self.long_prices.append(close)

        if len(self.long_prices) < self.long_window:
            return

        short_ma = sum(self.short_prices) / self.short_window
        long_ma  = sum(self.long_prices) / self.long_window

        if (short_ma > long_ma) and (not self.in_position):
            self.logger.info("📈 %s 金叉 BUY %.2f", dt.date(), close)
            self._submit(Order(next_seq(), bar["symbol"], "BUY", self.qty, close, dt))
            self.in_position = True

        elif (short_ma < long_ma) and self.in_position:
            self.logger.info("📉 %s 死叉 SELL %.2f", dt.date(), close)
            self._submit(Order(next_seq(), bar["symbol"], "SELL", self.qty, close, dt))
            self.in_position = False
