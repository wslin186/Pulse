"""
门面封装 - OesClientApi
只用 3 个方法：login / place_order / query_cash
"""
from __future__ import annotations
from pathlib import Path
from pulse.core.utils.logger import get_logger

# 引入官方原版类
from pulse.vendor.trade_api.oes_api import OesClientApi as _OesApi

class OesClientApi:
    def __init__(self, cfg_file: str | Path):
        self.cfg_file = str(cfg_file)
        self.logger   = get_logger("OES")
        self.api      = _OesApi(self.cfg_file)

    # ------------------ API ------------------ #
    def login(self) -> bool:
        ret = self.api.login()          # 官方方法名示例
        if ret != 0:
            self.logger.error("OES login fail ret=%s", ret)
            return False
        self.logger.info("✅ 登录成功")
        return True

    def query_cash(self):
        return self.api.query_cash()    # 假设官方有此方法

    def place_order(self, symbol: str, side: str, qty: int, price: float):
        """同步下单，side=BUY/SELL"""
        ord_id = self.api.send_order(symbol, side, qty, price)
        self.logger.info("下单完成 clOrdID=%s", ord_id)
        return ord_id

    def logout(self):
        self.api.logout()
        self.logger.info("已登出")
