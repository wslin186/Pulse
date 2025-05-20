# pulse/core/risk/risk_manager.py
from __future__ import annotations
from typing import List, Any
from pulse.core.utils.logger import get_logger
from pulse.core.execution.broker import LiveBroker
from pulse.core.execution.broker import OrderRequest  # 如果你用的是这个类型

class RiskManager:
    """动态风控：仓位不得超过当前可用资金 * max_pos_pct"""

    def __init__(self, broker: LiveBroker, max_pos_pct: float):
        """
        Args:
            broker       : LiveBroker 实例，用于查询最新资金和持仓
            max_pos_pct  : 单票最大仓位比例，例如 0.1 表示不能超过 10%
        """
        self.broker      = broker
        self.max_pos_pct = max_pos_pct
        self.logger      = get_logger("Risk")

    def validate(self, orders: List[OrderRequest]) -> List[OrderRequest]:
        """
        只对买单做金额校验：如果 o.qty*o.price > 当前可用资金 * max_pos_pct 就拒绝
        """
        valid = []
        # 每次都拉最新现金
        cash = self.broker.query_cash()
        for o in orders:
            if o.side.upper() == "BUY" and (o.qty * o.price) > cash * self.max_pos_pct:
                self.logger.warning(
                    "【风控】买 %s %d@%.2f 被拒：超过仓位上限(%.2f%%)，可用资金 %.2f",
                    o.symbol, o.qty, o.price, self.max_pos_pct * 100, cash
                )
                continue
            valid.append(o)
        return valid

    def update(self, fills: List[Any]) -> None:
        """
        成交后更新本地持仓缓存，如果你用 spi.get_positions() 就不需要
        """
        # 可选：根据需要来实现
        pass
