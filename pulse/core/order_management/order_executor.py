# core/order_management/order_executor.py
# -*- coding: utf-8 -*-
"""
订单发送 / 撤单 封装
-------------------------------------------------
全部使用 ClSeqNoManager 自动取号，并与 API 同步，无需手动传 clSeqNo
支持 market 传枚举或字符串 "SH"/"SZ"
"""
from typing import Optional, Union

from vendor.trade_api.oes_api import OesClientApi, OesOrdReqT, OesOrdCancelReqT
from vendor.trade_api.model import (
    eOesBuySellTypeT,
    eOesOrdTypeShT,
    eOesOrdTypeSzT,
    eOesMarketIdT,
)
from core.order_management.sequence import ClSeqNoManager


class OrderExecutor:
    def __init__(self, client: OesClientApi):
        """
        :param client: 已配置好账户和通道并启动的 OesClientApi 实例
        """
        self.client = client
        # 将客户端传给 ClSeqNoManager，用于读取和同步流水号
        self.cl_seq_manager = ClSeqNoManager(client)

    @staticmethod
    def _normalize_market(mkt: Union[int, str, eOesMarketIdT]) -> int:
        """
        将市场标识（int、枚举、"SH"/"SZ"）统一为 API 所需的 int
        """
        if isinstance(mkt, int):
            return mkt
        if isinstance(mkt, eOesMarketIdT):
            return int(mkt)  # type: ignore
        code = str(mkt).upper()
        if code == "SH":
            return int(eOesMarketIdT.SH)  # type: ignore
        if code == "SZ":
            return int(eOesMarketIdT.SZ)  # type: ignore
        raise ValueError(f"Unsupported market identifier: {mkt}")

    def send(
        self,
        symbol: str,
        qty: int,
        price: float,
        side: Union[eOesBuySellTypeT, int],
        market: Union[int, str, eOesMarketIdT],
        ord_type: Optional[Union[eOesOrdTypeShT, eOesOrdTypeSzT, int]] = None
    ) -> int:
        """
        下单
        :param symbol: 证券代码
        :param qty: 委托数量
        :param price: 委托价格
        :param side: 买卖类型，支持 enum 或 int
        :param market: 市场类型，支持 enum/int/"SH"/"SZ"
        :param ord_type: 订单类型，支持 enum 或 int，默认限价
        :return: API 返回值
        """
        req = OesOrdReqT()
        req.clSeqNo = self.cl_seq_manager.get_next_seq()
        req.invAcctId = getattr(self.client, "inv_acct_id", None)
        req.marketId = self._normalize_market(market)
        req.securityId = symbol
        req.ordQty = qty
        req.ordPrice = int(price * 1000)
        req.bsType = int(side)  # type: ignore
        if ord_type is None:
            if req.marketId == int(eOesMarketIdT.SH):  # type: ignore
                req.ordType = int(eOesOrdTypeShT.LMT)  # type: ignore
            else:
                req.ordType = int(eOesOrdTypeSzT.LMT)  # type: ignore
        else:
            req.ordType = int(ord_type)  # type: ignore
        return self.client.send_order(req)  # type: ignore

    def cancel(
        self,
        orig_cl_seq_no: int,
        market: Union[int, str, eOesMarketIdT]
    ) -> int:
        """
        撤单
        :param orig_cl_seq_no: 原始委托的流水号
        :param market: 市场类型，支持 enum/int/"SH"/"SZ"
        :return: API 返回值
        """
        req = OesOrdCancelReqT()
        req.clSeqNo = self.cl_seq_manager.get_next_seq()
        req.origClSeqNo = orig_cl_seq_no
        req.marketId = self._normalize_market(market)
        return self.client.cancel_order(req)  # type: ignore


