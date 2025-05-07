from __future__ import annotations
from typing import List
from collections import defaultdict

from pulse.core.utils.logger import get_logger
from pulse.core.execution.trade_models import Order


class RiskManager:
    """简单风控：仓位不得超过资金 * max_pos_pct"""

    def __init__(self, max_capital: float, max_pos_pct: float):
        self.max_capital  = max_capital
        self.max_pos_pct  = max_pos_pct
        self.positions    = defaultdict(int)
        self.logger       = get_logger("Risk")

    def validate(self, orders: List[Order]) -> List[Order]:
        valid = []
        for o in orders:
            # 暂时只检查买单金额
            if o.side == "BUY" and (o.qty * o.price) > self.max_capital * self.max_pos_pct:
                self.logger.warning("Buy %s 被拒: 超过单票限额", o.symbol)
                continue
            valid.append(o)
        return valid

    def update(self, fills):
        for f in fills:
            self.positions[f.symbol] += f.qty if f.side == "BUY" else -f.qty
