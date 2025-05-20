# -*- coding: utf-8 -*-
"""
pulse/scripts/mds_snapshot_trade.py

示例：MDS 查询快照行情 → 根据快照价格下单
"""
import sys
import threading
import time
from pathlib import Path

# 把项目根加入路径（Pulse/ 目录），这样才能 import pulse.api.trade
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
sys.path.append(str(PROJECT_ROOT))

from pulse.core.utils.logger import get_logger
from pulse.core.utils.config import load_yaml

# --- MDS 行情 SDK ---
from vendor.quote_api import (
    MdsClientApi,
    MdsAsyncApiChannelT,
    MDSAPI_CFG_DEFAULT_SECTION,
    MDSAPI_CFG_DEFAULT_KEY_TCP_ADDR
)

# --- OES 下单 SDK ---
from vendor.trade_api import (
    OesClientApi,
    OesOrdReqT,
    eOesMarketIdT,
    eOesBuySellTypeT,
    eOesOrdTypeSzT
)
from core.order_management.sequence import ClSeqNoManager

_LOG = get_logger("MdsSnapshotTrade")


class MdsQuerySpi:
    """
    只处理行情查询回调，把查询到的第一个快照放到 self.snapshot，然后 set 事件。
    """
    def __init__(self, evt: threading.Event):
        self._evt = evt
        self.snapshot: dict[str, float] = {}

    def on_qry_mkt_data_snapshot(self,
                                 channel: MdsAsyncApiChannelT,
                                 rsp_head,                                # 查询应答头
                                 snapshot,                               # 单只证券的快照体
                                 user_info):
        """单只快照查询回调"""
        code = snapshot.SecurityID.decode()
        price = snapshot.UpdatePrice / 10000.0  # 根据实际单位转换
        self.snapshot[code] = price
        _LOG.info("📋 快照[%s] Price=%.2f", code, price)
        # 只查询一只，拿到后就可以继续下单
        self._evt.set()
        return 0

    def on_qry_snapshot_list(self,
                             channel: MdsAsyncApiChannelT,
                             rsp_head,
                             snapshot_list,   # 列表快照
                             user_info):
        """批量快照查询回调"""
        for snap in snapshot_list:
            code = snap.SecurityID.decode()
            price = snap.UpdatePrice / 10000.0
            self.snapshot[code] = price
            _LOG.info("📋 快照[%s] Price=%.2f", code, price)
        self._evt.set()
        return 0


def run_snapshot_trade(cfg_path: Path):
    cfg = load_yaml(cfg_path)
    _LOG.info("加载配置：%s", cfg_path)

    symbols = cfg["symbols"]  # e.g. ["000001", "600000"]
    snapshot_evt = threading.Event()
    spi = MdsQuerySpi(snapshot_evt)

    # 1. 初始化 MDS API
    mds_api = MdsClientApi()
    if not mds_api.create_context(cfg["mds"]["config_file"]):
        _LOG.error("❌ MDS create_context 失败")
        return

    if not mds_api.register_spi(spi):
        _LOG.error("❌ MDS register_spi 失败")
        mds_api.release()
        return

    # 2. 添加查询通道
    tcp_ch = mds_api.add_channel_from_file(
        tag="qry_channel",
        cfg_file=cfg["mds"]["config_file"],
        cfg_section=MDSAPI_CFG_DEFAULT_SECTION,
        cfg_key=MDSAPI_CFG_DEFAULT_KEY_TCP_ADDR,
        user_info="qry_snapshot",
        reserve=None,
        auto_connect=True
    )
    if not tcp_ch:
        _LOG.error("❌ MDS add_channel_from_file 失败")
        mds_api.release()
        return

    # 3. 发起批量快照查询
    codes = ",".join(symbols)
    _LOG.info("开始查询快照：%s", codes)
    mds_api.query_snapshot_list(
        security_list=codes
    )

    # 4. 等待回调
    if not snapshot_evt.wait(timeout=5):
        _LOG.error("❌ 等待行情快照超时")
        mds_api.release()
        return
    prices = spi.snapshot
    mds_api.release()  # 结束 MDS 会话

    # 5. 根据第一个标的价格下单
    symbol = symbols[0]
    price = prices[symbol]
    order_price = int(price * 0.99 * 10000)  # 限价 0.99 倍现价

    _LOG.info("准备下单：%s @ %.2f (限价)", symbol, price * 0.99)

    # 6. 初始化 OES
    from vendor.trade_api import OesClientApi
    from pulse.api.trade import OesSpiLite  # 注意导入的是类名

    oes_api = OesClientApi(str(cfg["oes"]["config_file"]))

    # 实例化 SPI
    trade_spi = OesSpiLite()

    # 注册并启动
    oes_api.register_spi(trade_spi, add_default_channel=True)
    if not oes_api.start():
        _LOG.error("❌ OES 启动失败")
        return

    # 等通道就绪
    while not oes_api.is_channel_connected(oes_api.get_default_ord_channel()):
        time.sleep(0.2)
    while not oes_api.is_channel_connected(oes_api.get_default_rpt_channel()):
        time.sleep(0.2)
    _LOG.info("✅ OES 通道就绪")

    # 7. 下单
    cl_mgr = ClSeqNoManager(oes_api)
    seq = cl_mgr.get_next_seq()
    req = OesOrdReqT(
        clSeqNo=seq,
        mktId=eOesMarketIdT.OES_MKT_SZ_ASHARE,
        securityId=symbol.encode(),
        bsType=eOesBuySellTypeT.OES_BS_TYPE_BUY,
        ordType=eOesOrdTypeSzT.OES_ORD_TYPE_SZ_LMT,
        ordQty=100,
        ordPrice=order_price
    )
    ret = oes_api.send_order(oes_api.get_default_ord_channel(), req)
    _LOG.info("📤 发单 ret=%d, seq=%d", ret, seq)

    # 8. 等待成交或挂单回报（可在 OesSpiLite 内部触发事件）
    time.sleep(3)
    oes_api.release()
    _LOG.info("🎉 全流程结束")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser("MDS 快照查询下单示例")
    parser.add_argument("-c", "--config", type=Path,
                        required=True, help="YAML 配置文件路径")
    args = parser.parse_args()
    run_snapshot_trade(args.config)
