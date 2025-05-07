from __future__ import annotations
import importlib
from abc import ABC, abstractmethod
from typing import Dict, Any, List

import pandas as pd
from pulse.core.execution.trade_models import Order

from pulse.core.utils.logger import get_logger


class BaseStrategy(ABC):
    """所有策略基类"""

    def __init__(self, name: str, params: Dict[str, Any] | None = None):
        self.name   = name
        self.params = params or {}
        self.logger = get_logger(name)
        self._orders: List[Order] = []      # <- 新增

    # ------------ 业务接口 ------------ #
    @abstractmethod
    def on_bar(self, bar: pd.Series) -> None: ...

    def on_tick(self, tick: Dict[str, Any]) -> None:
        pass

    # ---------- 订单提交 & 读取 ---------- #
    def _submit(self, order: Order) -> None:
        self._orders.append(order)

    def pop_orders(self) -> List[Order]:
        orders, self._orders = self._orders, []
        return orders

    # ---------- 工厂方法 ---------- #
    @classmethod
    def from_config(cls, cfg: Dict[str, Any]) -> "BaseStrategy":
        dotted = cfg["class"]
        mod_name, class_name = dotted.rsplit(".", 1)
        module = importlib.import_module(mod_name)
        klass  = getattr(module, class_name)
        return klass(name=class_name, params=cfg.get("params", {}))
