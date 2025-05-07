from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import List, Dict

import pandas as pd

from pulse.core.data.market_data_provider import MarketDataProvider
from pulse.core.strategy.base_strategy import BaseStrategy
from pulse.core.execution.broker import SimBroker
from pulse.core.risk.risk_manager import RiskManager
from pulse.core.utils.logger import get_logger
from pulse.core.execution.trade_models import Order, Fill


@dataclass
class BacktestReport:
    equity_curve: pd.Series
    metrics: Dict[str, float]

    def to_html(self, path: str) -> None:
        html = f"<h1>Backtest Report</h1>\n<h2>Metrics</h2>\n"
        html += "<ul>" + "".join(f"<li>{k}: {v:.3f}</li>" for k, v in self.metrics.items()) + "</ul>"
        html += self.equity_curve.to_frame("Equity").to_html()
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)


class Backtester:
    """单品种日线级回测"""

    def __init__(self,
                 strategy: BaseStrategy,
                 broker: SimBroker,
                 risk_mgr: RiskManager,
                 data_provider: MarketDataProvider,
                 symbol: str):
        self.strategy   = strategy
        self.broker     = broker
        self.risk       = risk_mgr
        self.data       = data_provider
        self.symbol     = symbol
        self.logger     = get_logger("Backtester")

    def run(self, start: str, end: str) -> BacktestReport:
        df = self.data.load_bars(self.symbol, start, end)
        df["symbol"] = self.symbol      # 供策略读取
        equity = []

        for idx, bar in df.iterrows():
            # 1) 策略计算
            self.strategy.on_bar(bar)

            # 2) 取订单 -> 风控 -> 撮合
            orders: List[Order] = self.strategy.pop_orders()
            orders = self.risk.validate(orders)
            fills: List[Fill]  = self.broker.place_orders(orders, bar_close=bar["close"])
            self.risk.update(fills)

            # 3) 记录权益
            equity.append(self.broker.equity({self.symbol: bar["close"]}))

        equity_curve = pd.Series(equity, index=df.index, name="Equity")
        metrics = self._calc_metrics(equity_curve)
        self.logger.info("回测完毕 %s ~ %s  Metrics: %s", start, end, metrics)
        return BacktestReport(equity_curve, metrics)

    @staticmethod
    def _calc_metrics(eq: pd.Series) -> Dict[str, float]:
        ret = eq.pct_change().dropna()
        cum_ret = eq.iloc[-1] / eq.iloc[0] - 1
        sharpe  = (ret.mean() / ret.std()) * (252 ** 0.5) if ret.std() else 0
        mdd     = ((eq.cummax() - eq) / eq.cummax()).max()
        return {"cum_return": cum_ret, "sharpe": sharpe, "max_drawdown": mdd}
