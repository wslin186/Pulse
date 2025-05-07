from __future__ import annotations

from collections import defaultdict
from typing import List, Dict

from pulse.core.utils.logger import get_logger
from core.order_management.sequence import next_seq
from .trade_models import Order, Fill


class SimBroker:
    """极简撮合：以当前 bar 收盘价立即成交"""

    def __init__(self, initial_cash: float):
        self.cash      = initial_cash
        self.positions = defaultdict(int)   # symbol -> qty
        self.logger    = get_logger("SimBroker")
        self.fills: List[Fill] = []

    # -------- API -------- #
    def place_orders(self, orders: List[Order], bar_close: float) -> List[Fill]:
        fills: List[Fill] = []
        for o in orders:
            if o.side == "BUY" and self.cash < o.qty * bar_close:
                self.logger.warning("现金不足，拒绝 BUY %s x%s", o.symbol, o.qty)
                continue
            # 更新资金 & 持仓
            if o.side == "BUY":
                self.cash -= o.qty * bar_close
                self.positions[o.symbol] += o.qty
            else:  # SELL
                self.cash += o.qty * bar_close
                self.positions[o.symbol] -= o.qty
            f = Fill(o.id, o.symbol, o.side, o.qty, bar_close, o.dt)
            fills.append(f)
            self.logger.debug("成交 %s", f)
        self.fills.extend(fills)
        return fills

    def equity(self, last_price: Dict[str, float]) -> float:
        eq = self.cash
        for sym, qty in self.positions.items():
            eq += qty * last_price.get(sym, 0)
        return eq

# ------------------------------------------------------------------
# 占位实现：先继承 SimBroker，保留接口，后续再完善实时下单逻辑
# ------------------------------------------------------------------
# 在文件底部追加 / 替换旧占位

class LiveBroker(SimBroker):
    """实盘 OES 下单（最小实现）"""

    def __init__(self, initial_cash: float, api_cfg: dict):
        super().__init__(initial_cash)
        # TODO: 用 api_cfg 初始化 OES 连接
        from pulse.api.trade.oes_api import OesClientApi  # 假设已封装；若没封装先保留 TODO
        self.api = OesClientApi(api_cfg.get("cfg_file", "./config/oes_client_stk.conf"))
        self.api.login()
        self.logger.info("✅ OES 交易通道已连接")

    @classmethod
    def from_config(cls, cfg):
        return cls(initial_cash=cfg.get("initial_cash", 0), api_cfg=cfg)

    async def send_orders(self, orders):
        """异步发送订单"""
        for o in orders:
            # TODO: 封装至 api.place_order; 简化示例
            self.logger.info("下单: %s %s x%s @%.2f", o.side, o.symbol, o.qty, o.price)
            # 假设立即成交
            self.place_orders([o], bar_close=o.price)

    async def fetch_fills(self):
        """轮询成交回报（示例直接返回 self.fills 并清空）"""
        fills, self.fills = self.fills, []
        return fills
