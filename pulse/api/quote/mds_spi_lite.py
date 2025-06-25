# -*- coding: utf-8 -*-
"""
针对 A 股 L1 快照的 MDS Lite SPI
"""
import threading
import asyncio
from typing import List, Optional, Union

from vendor.quote_api import (
    MdsClientSpi,
    MdsAsyncApiChannelT,
    eMdsExchangeIdT,
    eMdsMdProductTypeT,
    eMdsSubscribeModeT,
    eMdsSubscribeDataTypeT,
)
from vendor.quote_api import MDSAPI_CFG_DEFAULT_SECTION, MDSAPI_CFG_DEFAULT_KEY_TCP_ADDR
from vendor.quote_api.model import MdsSecurityStatusMsgT, MdsTradingSessionStatusMsgT

from pulse.core.data.types import MarketSnapshot
from pulse.core.utils.logger import get_logger

_LOG = get_logger("MdsSpiLite")


class MdsSpiLite(MdsClientSpi):
    """
    精简版 SPI：只订阅指定 A 股的 L1 快照，转换成 MarketSnapshot 推到队列。
    """
    def __init__(
        self,
        config_file: str,
        subscribe_codes: List[str],
        snapshot_queue: Optional[asyncio.Queue] = None,
        first_snapshot_evt: Optional[threading.Event] = None
    ):
        super(MdsSpiLite, self).__init__()
        self.config_file = config_file
        self.subscribe_codes = subscribe_codes
        self.snapshot_queue = snapshot_queue or asyncio.Queue()
        self.first_snapshot_evt = first_snapshot_evt or threading.Event()

    def on_connect(self, channel: MdsAsyncApiChannelT, user_info: Union[str,int,object]) -> int:
        """
        连接后自动订阅 L1 快照
        """
        _LOG.info("✅ MDS 已连接，开始订阅 L1 快照：%s", self.subscribe_codes)

        # 拆分上交所/深交所
        sse = [c for c in self.subscribe_codes if c.startswith("6")]
        szse = [c for c in self.subscribe_codes if not c.startswith("6")]

        # data_types: 只订阅 L1 快照
        dt = eMdsSubscribeDataTypeT.MDS_SUB_DATA_TYPE_INDEX_SNAPSHOT \
             | eMdsSubscribeDataTypeT.MDS_SUB_DATA_TYPE_OPTION_SNAPSHOT \
             | eMdsSubscribeDataTypeT.MDS_SUB_DATA_TYPE_L2_SNAPSHOT  # 这里也可加 L2 快照

        # 上海
        if sse:
            ret = self.mds_api.subscribe_by_string(
                channel=channel,
                security_list=",".join(sse),
                delimiter=",",
                exchange_id=eMdsExchangeIdT.MDS_EXCH_SSE,
                product_type=eMdsMdProductTypeT.MDS_MD_PRODUCT_TYPE_STOCK,
                sub_mode=eMdsSubscribeModeT.MDS_SUB_MODE_SET,
                data_types=eMdsSubscribeDataTypeT.MDS_SUB_DATA_TYPE_L2_SNAPSHOT  # L1 在SDK里属于L2快照类型
            )
            _LOG.info("上海订阅结果: %s", ret)

        # 深圳
        if szse:
            ret = self.mds_api.subscribe_by_string(
                channel=channel,
                security_list=",".join(szse),
                delimiter=",",
                exchange_id=eMdsExchangeIdT.MDS_EXCH_SZSE,
                product_type=eMdsMdProductTypeT.MDS_MD_PRODUCT_TYPE_STOCK,
                sub_mode=eMdsSubscribeModeT.MDS_SUB_MODE_SET,
                data_types=eMdsSubscribeDataTypeT.MDS_SUB_DATA_TYPE_L2_SNAPSHOT
            )
            _LOG.info("深圳订阅结果: %s", ret)

        return 0

    def _push_snapshot(self, snap: MarketSnapshot):
        """内部统一推送并通知首条快照到达"""
        try:
            self.snapshot_queue.put_nowait(snap)
        except Exception:
            _LOG.exception("❌ 推送 MarketSnapshot 失败")
        if not self.first_snapshot_evt.is_set():
            self.first_snapshot_evt.set()

    def on_market_data_snapshot_full_refresh(
        self,
        channel: MdsAsyncApiChannelT,
        msg_head,
        msg_body,           # MdsMktDataSnapshotT
        user_info
    ) -> int:
        """
        L1 全量快照回调，把 msg_body 转为 MarketSnapshot 并推队列
        """
        try:
            snap = MarketSnapshot(
                symbol=msg_body.stock.SecurityID.decode(),
                last_price=msg_body.stock.TradePx / 10000.0,
                open_price=msg_body.stock.OpenPx / 10000.0,
                high_price=msg_body.stock.HighestPx / 10000.0,
                low_price=msg_body.stock.LowestPx / 10000.0,
                bid_price=msg_body.stock.BidLevels[0].Price / 10000.0,
                ask_price=msg_body.stock.OfferLevels[0].Price / 10000.0,
                bid_qty=msg_body.stock.BidLevels[0].Volume,    # SDK 字段名或 Volume
                ask_qty=msg_body.stock.OfferLevels[0].Volume,
                volume=msg_body.stock.TotalVolumeTrade,
                turnover=msg_body.stock.TotalValueTrade / 10000.0,
                update_time=msg_body.stock.UpdateTime  # 如需可转换为 datetime
            )
            self._push_snapshot(snap)
        except Exception:
            _LOG.exception("❌ 处理快照回调失败")
        return 0

    def on_connect_failed(self, channel, user_info):
        _LOG.warning("⚠️ MDS 连接失败，将自动重试")
        return 0

    def on_disconnect(self, channel, user_info):
        _LOG.warning("⚠️ MDS 连接已断开，将自动重连")
        return 0

    # —— 市场状态类回调 ——
    def on_security_status(self, channel, msg_head, msg_body: MdsSecurityStatusMsgT, user_info):
        try:
            code = msg_body.SecurityID.decode()
            status = msg_body.SecurityStatusFlag
            _LOG.debug("证券状态变动 %s => 0x%X", code, status)
        except Exception:
            _LOG.exception("解析证券状态失败")
        return 0

    def on_trading_session_status(self, channel, msg_head, msg_body: MdsTradingSessionStatusMsgT, user_info):
        try:
            _LOG.info("交易节状态 %s | %s", msg_body.ExchID, msg_body.TradingSessionID)
        except Exception:
            _LOG.exception("解析交易节状态失败")
        return 0

    # —— Level2 逐笔示例回调 ——
    def on_l2_tick_trade(self, channel, msg_head, msg_body, user_info):
        # 这里只简单输出，用户可自行扩展写入队列
        try:
            _LOG.debug("逐笔成交 %s @ %.2f x %d", msg_body.SecurityID.decode(), msg_body.TradePrice/10000.0, msg_body.TradeQty)
        except Exception:
            pass
        return 0

    def on_l2_tick_order(self, channel, msg_head, msg_body, user_info):
        return 0

    def on_l2_market_data_snapshot(self, channel, msg_head, msg_body, user_info):
        return 0

    def on_l2_best_orders_snapshot(self, channel, msg_head, msg_body, user_info):
        return 0

    def on_l2_market_overview(self, channel, msg_head, msg_body, user_info):
        return 0

    # 其余未用回调直接返回 0 即可，保持与基类兼容
    def on_market_index_snapshot_full_refresh(self, channel, msg_head, msg_body, user_info):
        return 0

    def on_market_option_snapshot_full_refresh(self, channel, msg_head, msg_body, user_info):
        return 0

    def on_tick_channel_heart_beat(self, channel, msg_head, msg_body, user_info):
        return 0
