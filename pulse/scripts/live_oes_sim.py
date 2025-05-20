# -*- coding: utf-8 -*-
"""
live_oes_sim.py

MDS 行情订阅 + OES 模拟环境下单示例脚本
打印每条快照、策略意向、风控决策和下单信号
针对云环境历史回放加入队列超时机制
"""
import sys
import time
import threading
import asyncio
from pathlib import Path
from typing import Any

# 项目根路径
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "pulse" / "vendor"))

# MDS SDK
from vendor.quote_api import (
    MdsClientApi,
    MDSAPI_CFG_DEFAULT_SECTION,
    MDSAPI_CFG_DEFAULT_KEY_TCP_ADDR,
    MdsAsyncApiChannelT,
)
from pulse.api.quote.mds_spi_lite import MdsSpiLite

# OES SDK
from vendor.trade_api import OesClientApi
from pulse.api.trade.oes_spi_lite import OesSpiLite

# 核心组件
from pulse.core.utils.config           import load_yaml
from pulse.core.strategy.base_strategy import BaseStrategy
from pulse.core.execution.broker       import LiveBroker
from pulse.core.risk.risk_manager      import RiskManager
from pulse.core.utils.logger           import get_logger

_LOG = get_logger("LiveOesSim")
trade_evt = threading.Event()

async def run_live_oes_sim(cfg: dict[str, Any]):
    # 1) MDS 初始化
    mds_conf = PROJECT_ROOT / cfg["data"]["config_file"]
    _LOG.info("📂 加载 MDS 配置: %s", mds_conf)
    mds_api = MdsClientApi()
    if not mds_api.create_context(str(mds_conf)):
        _LOG.error("❌ MDS init 失败: %s", mds_conf)
        return

    # 注册 SPI 并启动订阅
    mds_spi = MdsSpiLite(
        config_file=str(mds_conf),
        subscribe_codes=cfg["data"]["symbols"]
    )
    mds_api.register_spi(mds_spi, add_default_channel=False)
    tcp_ch: MdsAsyncApiChannelT = mds_api.add_channel_from_file(
        "tcp_channel",
        str(mds_conf),
        MDSAPI_CFG_DEFAULT_SECTION,
        MDSAPI_CFG_DEFAULT_KEY_TCP_ADDR,
        "subscribe_all",
        None,
        True
    )
    if not tcp_ch or not mds_api.start():
        _LOG.error("❌ MDS 启动失败")
        return
    _LOG.info("✅ MDS 已启动，订阅: %s", cfg["data"]["symbols"])

    # 2) OES 初始化
    oes_conf = PROJECT_ROOT / cfg["broker"]["config_file"]
    _LOG.info("📂 加载 OES 配置: %s", oes_conf)
    oes_api = OesClientApi(str(oes_conf))
    oes_spi = OesSpiLite()
    oes_spi._done_evt = trade_evt
    oes_api.register_spi(oes_spi, add_default_channel=True)
    if not oes_api.start():
        _LOG.error("❌ OES 启动失败")
        return

    # 等待通道就绪
    while not oes_api.is_channel_connected(oes_api.get_default_ord_channel()):
        time.sleep(0.1)
    while not oes_api.is_channel_connected(oes_api.get_default_rpt_channel()):
        time.sleep(0.1)
    _LOG.info("✅ OES 通道就绪")

    # 3) Broker、策略、风控
    broker   = LiveBroker(api=oes_api, spi=oes_spi)
    strategy = BaseStrategy.from_config(cfg["strategy"])
    risk     = RiskManager(broker=broker, max_pos_pct=cfg["risk"]["max_pos_pct"])

    # 4) 等待首条快照
    _LOG.info("⏳ 等待首条快照…")
    await asyncio.get_event_loop().run_in_executor(
        None, mds_spi.first_snapshot_evt.wait, 30
    )
    _LOG.info("✅ 收到首条快照")

    # 5) 实时循环 (附加超时)
    snap_count = 0
    while True:
        try:
            snap = await asyncio.wait_for(mds_spi.snapshot_queue.get(), timeout=5.0)
        except asyncio.TimeoutError:
            _LOG.debug("⚠️ 5s 未收到新快照，继续")
            continue

        snap_count += 1
        _LOG.info("📑 第%d条 快照: %s %.2f", snap_count, snap.symbol, snap.last_price)

        orders = strategy.on_snapshot(snap)
        if orders:
            _LOG.info("💡 意向 %d 单", len(orders))
        valid = risk.validate(orders)
        if not valid and orders:
            _LOG.warning("❌ 风控拒绝")
            continue
        for o in valid:
            seq = broker.send_order(o)
            if seq <= 0:
                _LOG.error("✖️ 发单失败 %s", o.symbol)
                continue
            _LOG.info("▶ 发单 OK seq=%d", seq)
            trade_evt.clear()
            if trade_evt.wait(30):
                fills = broker.fetch_fills()
                _LOG.info("✅ 回报: %s", fills)
                risk.update(fills)
            else:
                _LOG.warning("⚠️ 未收到成交回报 seq=%d", seq)

if __name__ == "__main__":
    cfg = load_yaml(PROJECT_ROOT / "config" / "live_oes_sim.yaml")
    asyncio.run(run_live_oes_sim(cfg))
