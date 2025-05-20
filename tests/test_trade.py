# -*- coding: utf-8 -*-
"""test—.py —— 2 限价买入 + 合理卖出 + 撤单的完整流程示例"""

import time
import threading
from pathlib import Path
import sys
# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from pulse.vendor.trade_api import (
    OesClientApi,
    OesOrdReqT, OesOrdCancelReqT,
    eOesMarketIdT,
    eOesBuySellTypeT,
    eOesOrdTypeSzT,
    eOesSubscribeReportTypeT
)
from pulse.core.order_management.sequence import ClSeqNoManager
from pulse.core.utils.logger import get_logger
from pulse.api.trade.oes_spi_lite import OesSpiLite

log = get_logger("TradeTest")
CONF_FILE = Path("../config/oes_client_stk.conf").resolve()

class TestSpi(OesSpiLite):
    def __init__(self, cash_evt: threading.Event, done_evt: threading.Event):
        super().__init__()
        self._cash_evt = cash_evt
        self._done_evt = done_evt

    def on_rpt_connect(self, channel, user_info):
        tag = channel.pChannelCfg.contents.channelTag.decode()
        log.info("📡 回报通道 [%s] 已连接，发送同步订阅指令…", tag)
        self.oes_api.send_report_synchronization(
            channel,
            subscribe_env_id=0,
            subscribe_rpt_types=0,
            last_rpt_seq_num=sys.maxsize
        )
        return 0

    def on_cash_asset_variation(self, channel, msg_head, rpt_msg_head, rpt_msg_body, user_info):
        super().on_cash_asset_variation(channel, msg_head, rpt_msg_head, rpt_msg_body, user_info)
        self._cash_evt.set()
        return 0

    def on_query_cash_asset(self, channel, msg_head, msg_body, cursor, user_info):
        self._cash_evt.set()
        return 0

    def on_trade_report(self, channel, msg_head, rpt_msg_head, rpt_msg_body, user_info):
        super().on_trade_report(channel, msg_head, rpt_msg_head, rpt_msg_body, user_info)
        self._done_evt.set()
        return 0


def main() -> None:
    cash_evt = threading.Event()
    done_evt = threading.Event()

    api = OesClientApi(str(CONF_FILE))
    spi = TestSpi(cash_evt, done_evt)
    if not api.register_spi(spi, add_default_channel=True) or not api.start():
        log.error("❌ API 初始化失败")
        return

    # 等通道就绪
    while not api.is_channel_connected(api.get_default_ord_channel()):
        log.info("⏳ 等待委托通道连接…"); time.sleep(1)
    while not api.is_channel_connected(api.get_default_rpt_channel()):
        log.info("⏳ 等待回报通道连接…"); time.sleep(1)
    log.info("✅ 通道全部就绪")

    # 登录后立即查资金，获取初始快照
    api.query_cash_asset()
    cash_evt.wait(timeout=3); cash_evt.clear()

    cl_mgr = ClSeqNoManager(api)

    # 价格设置
    reasonable_price = 10.00  # 合理价格 (参考当前行情)
    bad_price = 8.00          # 不合理价格 (远低于卖一)
    rp_int = int(reasonable_price * 10000)
    bp_int = int(bad_price * 10000)

    # ----------------------------------------------------------------
    # 1) 限价买入 200 股 (合理价)
    # ----------------------------------------------------------------
    seq1 = cl_mgr.get_next_seq()
    req1 = OesOrdReqT(
        clSeqNo=seq1,
        mktId=eOesMarketIdT.OES_MKT_SZ_ASHARE,
        securityId=b"000001",
        bsType=eOesBuySellTypeT.OES_BS_TYPE_BUY,
        ordType=eOesOrdTypeSzT.OES_ORD_TYPE_SZ_LMT,
        ordQty=200,
        ordPrice=rp_int
    )
    ret1 = api.send_order(api.get_default_ord_channel(), req1)
    log.info("📈 [限价买入合理] 单号=%d, qty=200, price=%.2f, ret=%d", seq1, reasonable_price, ret1)
    time.sleep(1)  # 等待 "已接收" 回报

    # ----------------------------------------------------------------
    # 2) 限价买入 100 股 (不合理价)
    # ----------------------------------------------------------------
    seq2 = cl_mgr.get_next_seq()
    req2 = OesOrdReqT(
        clSeqNo=seq2,
        mktId=eOesMarketIdT.OES_MKT_SZ_ASHARE,
        securityId=b"000001",
        bsType=eOesBuySellTypeT.OES_BS_TYPE_BUY,
        ordType=eOesOrdTypeSzT.OES_ORD_TYPE_SZ_LMT,
        ordQty=100,
        ordPrice=bp_int
    )
    ret2 = api.send_order(api.get_default_ord_channel(), req2)
    log.info("📌 [限价买入挂单] 单号=%d, qty=100, price=%.2f, ret=%d", seq2, bad_price, ret2)
    time.sleep(1)

    # ----------------------------------------------------------------
    # 3) 限价卖出 100 股 (合理价)
    # ----------------------------------------------------------------
    seq3 = cl_mgr.get_next_seq()
    req3 = OesOrdReqT(
        clSeqNo=seq3,
        mktId=eOesMarketIdT.OES_MKT_SZ_ASHARE,
        securityId=b"000001",
        bsType=eOesBuySellTypeT.OES_BS_TYPE_SELL,
        ordType=eOesOrdTypeSzT.OES_ORD_TYPE_SZ_LMT,
        ordQty=100,
        ordPrice=rp_int
    )
    ret3 = api.send_order(api.get_default_ord_channel(), req3)
    log.info("🔄 [限价卖出合理] 单号=%d, qty=100, price=%.2f, ret=%d", seq3, reasonable_price, ret3)
    if done_evt.wait(timeout=10):
        done_evt.clear()
        api.query_cash_asset(); cash_evt.wait(timeout=3); cash_evt.clear()
    else:
        log.error("❌ 限价卖单 %d 未成交", seq3)

    # ----------------------------------------------------------------
    # 4) 撤销第2步的限价买单 (不合理价)
    # ----------------------------------------------------------------
    seq4 = cl_mgr.get_next_seq()
    cancel_req = OesOrdCancelReqT(
        clSeqNo=seq4,
        mktId=eOesMarketIdT.OES_MKT_SZ_ASHARE,
        origClOrdId=seq2
    )
    ret4 = api.send_cancel_order(api.get_default_ord_channel(), cancel_req)
    log.info("🚮 [撤单] 单号=%d, 撤销挂单 %d, ret=%d", seq4, seq2, ret4)

    api.release()
    log.info("🎉 测试结束")

if __name__ == "__main__":
    main()