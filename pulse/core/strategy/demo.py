# pulse/core/strategy/demo.py
# -*- coding: utf-8 -*-
from pulse.core.strategy.base_strategy import BaseStrategy
from pulse.core.execution.broker import OrderRequest

class DemoStrategy(BaseStrategy):
    """
    简单示例策略：当最新价低于开盘价 * buy_threshold 时买入；
    当最新价高于开盘价 * sell_threshold 时卖出。
    """

    def on_bar(self, bar) -> list[OrderRequest]:
        """
        BaseStrategy 要求实现的 on_bar 方法。
        如果你不做基于 bar 的策略，可以直接返回空列表。
        """
        return []

    def on_snapshot(self, snap) -> list[OrderRequest]:
        bt = self.params.get("buy_threshold", 0.995)
        st = self.params.get("sell_threshold", 1.005)

        orders: list[OrderRequest] = []

        # 如果跌破买入阈值，下多头100股
        if snap.last_price < snap.open_price * bt:
            orders.append(
                OrderRequest(
                    symbol=snap.symbol,
                    side="buy",
                    qty=100,
                    price=snap.last_price
                )
            )
        # 如果突破卖出阈值，下空头100股
        elif snap.last_price > snap.open_price * st:
            orders.append(
                OrderRequest(
                    symbol=snap.symbol,
                    side="sell",
                    qty=100,
                    price=snap.last_price
                )
            )

        return orders
