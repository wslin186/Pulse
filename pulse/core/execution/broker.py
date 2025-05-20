# pulse/core/execution/broker.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, List, Dict

from core.order_management.sequence import ClSeqNoManager
from vendor.trade_api import (
    OesClientApi,
    OesOrdReqT,
    OesOrdCancelReqT,
    eOesMarketIdT,
    eOesBuySellTypeT,
    eOesOrdTypeSzT,
)


@dataclass
class OrderRequest:
    """
    统一的订单请求类型
    """
    symbol: str
    side: str    # "buy" 或 "sell"
    qty: int
    price: float


class LiveBroker:
    """
    实盘 Broker —— 以 OES 为例
    - send_order: 下限价单
    - cancel_order: 撤单
    - fetch_fills: 取成交回报
    - query_cash: 查询资金
    - query_positions: 查询持仓
    """
    def __init__(self, api: OesClientApi, spi: Any):
        self._api = api
        self._spi = spi
        self._cl_mgr = ClSeqNoManager(self._api)

    def send_order(self, order: OrderRequest) -> int:
        """
        发送限价单，返回 clSeqNo（<0 表示失败）
        """
        seq = self._cl_mgr.get_next_seq()
        req = OesOrdReqT(
            clSeqNo=seq,
            mktId=eOesMarketIdT.OES_MKT_SZ_ASHARE,
            securityId=order.symbol.encode(),
            bsType=(
                eOesBuySellTypeT.OES_BS_TYPE_BUY
                if order.side == "buy"
                else eOesBuySellTypeT.OES_BS_TYPE_SELL
            ),
            ordType=eOesOrdTypeSzT.OES_ORD_TYPE_SZ_LMT,
            ordQty=order.qty,
            ordPrice=int(order.price * 10000),
        )
        ret = self._api.send_order(self._api.get_default_ord_channel(), req)
        return seq if ret == 0 else -1

    def cancel_order(self, orig_seq: int) -> int:
        """
        撤单：orig_seq 是之前 send_order 返回的 clSeqNo
        返回本次撤单的 clSeqNo（<0 表示失败）
        """
        cancel_seq = self._cl_mgr.get_next_seq()
        cancel_req = OesOrdCancelReqT(
            clSeqNo=cancel_seq,
            mktId=eOesMarketIdT.OES_MKT_SZ_ASHARE,
            origClOrdId=orig_seq
        )
        ret = self._api.send_cancel_order(
            self._api.get_default_ord_channel(), cancel_req
        )
        return cancel_seq if ret == 0 else -1

    def fetch_fills(self) -> List[Any]:
        """
        获取成交回报列表。假设你的 OesSpiLite 实现了 get_fills()，
        并在 on_trade_report 中缓存了成交数据。
        """
        return self._spi.get_fills()

    def query_cash(self) -> float:
        """
        查询最新资金，可用余额等。
        假设 OesClientApi.query_cash_asset() 返回一个带
        'availableBalance' 属性的结构体或 dict。
        """
        resp = self._api.query_cash_asset()
        # 根据实际返回类型改下面一行：
        if hasattr(resp, "availableBalance"):
            return resp.availableBalance
        if isinstance(resp, dict) and "availableBalance" in resp:
            return resp["availableBalance"]
        # 否则直接尝试转成 float
        return float(resp)

    def query_positions(self) -> Dict[str, int]:
        """
        查询持仓，返回 {symbol: qty}
        假设你的 OesSpiLite 在 on_position_report 中缓存了
        positions，并提供 get_positions() 方法。
        """
        # 如果你实现了 SPI.get_positions():
        if hasattr(self._spi, "get_positions"):
            return self._spi.get_positions()

        # 或者调用 SDK 的同步接口（如存在）
        # pos_list = self._api.query_position_list()
        # return { p.SecurityID.decode(): p.TotalQty for p in pos_list }

        # 否则返回空
        return {}
