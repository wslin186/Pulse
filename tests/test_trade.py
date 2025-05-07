# -*- coding: utf-8 -*-
"""test_oes_nockpt.py —— 简单委托 + 资金快照（无 checkpoint / hook）"""

import time
import threading
from pathlib import Path

from vendor.trade_api import (
    OesClientApi, OesOrdReqT,
    eOesMarketIdT, eOesBuySellTypeT, eOesOrdTypeT
)
from core.order_management.sequence    import ClSeqNoManager
from core.order_management.order_manager import send_order
from core.utils.logger import get_logger
from api.trade.oes_spi_lite import OesSpiLite

log = get_logger("TradeTest")
CONF_FILE = Path("../config/oes_client_stk.conf").resolve()


# =================================================================
# SPI：只触发现金 / 成交事件
# =================================================================
class TestSpi(OesSpiLite):
    def __init__(self, cash_evt: threading.Event, done_evt: threading.Event):
        super().__init__()
        self._cash_evt, self._done_evt = cash_evt, done_evt

    def on_cash_asset_variation(self, *a):
        super().on_cash_asset_variation(*a)
        self._cash_evt.set(); return 0

    def on_query_cash_asset(self, *a):
        self._cash_evt.set(); return 0

    def on_trade_report(self, *a):
        super().on_trade_report(*a)
        self._done_evt.set(); return 0


def main() -> None:
    cash_evt, done_evt = threading.Event(), threading.Event()

    api = OesClientApi(str(CONF_FILE))
    spi = TestSpi(cash_evt, done_evt)

    if not api.register_spi(spi, add_default_channel=True) or not api.start():
        log.error("❌ API 初始化失败"); return

    # 等通道就绪
    while not api.is_channel_connected(api.get_default_ord_channel()):
        log.info("⏳ 等待委托通道连接…"); time.sleep(1)
    while not api.is_channel_connected(api.get_default_rpt_channel()):
        log.info("⏳ 等待回报通道连接…"); time.sleep(1)
    log.info("✅ 通道全部就绪")

    # 登录后立即查资金
    api.query_cash_asset(); cash_evt.wait(timeout=3); cash_evt.clear()

    cl_mgr = ClSeqNoManager(api)

    # ----------- 下单演示 -----------
    ret = send_order(
        api, cl_mgr,
        mkt=eOesMarketIdT.OES_MKT_SZ_ASHARE,
        security_id="000001",
        side=eOesBuySellTypeT.OES_BS_TYPE_BUY,
        qty=100, price=9.99        # send_order 内部 ×10000
    )
    if ret < 0:
        log.warning(f"⚠️ 下单失败 ret={ret} err={api.get_last_error()}")
        api.release(); return
    log.info("📨 已发委托，等待成交回报…")

    if not done_evt.wait(timeout=10):
        log.warning("⚠️ 10 秒内未收到成交回报")
    else:
        api.query_cash_asset(); cash_evt.wait(timeout=3)

    api.release(); log.info("🎉 测试结束")


if __name__ == "__main__":
    main()
