# core/order_management/order_manager.py
# -*- coding: utf-8 -*-
"""
对外统一接口：send_order 和 cancel_order
内部调用 OrderExecutor
"""
from typing import Union

from vendor.trade_api.model import eOesBuySellTypeT
from vendor.trade_api.oes_api import OesClientApi
from core.order_management.order_executor import OrderExecutor


class OrderManager:
    def __init__(self, client: OesClientApi):
        """
        :param client: 已初始化并登录的 OesClientApi 实例
        """
        self.executor = OrderExecutor(client)

    def send_order(
        self,
        symbol: str,
        quantity: int,
        price: float,
        side: Union[eOesBuySellTypeT, int],
        market: Union[int, str] = "SH"
    ) -> int:
        """
        发送委托
        :param symbol: 证券代码
        :param quantity: 委托数量
        :param price: 委托价格
        :param side: 买卖类型，支持 enum 或 int
        :param market: 市场类型，支持 enum/int/"SH"/"SZ"
        :return: API 返回值
        """
        if not isinstance(side, eOesBuySellTypeT):
            side = eOesBuySellTypeT(side)  # type: ignore
        return self.executor.send(symbol, quantity, price, side, market)

    def cancel_order(
        self,
        orig_cl_seq_no: int,
        market: Union[int, str] = "SH"
    ) -> int:
        """
        撤销委托
        :param orig_cl_seq_no: 原始委托流水号
        :param market: 市场类型，支持 enum/int/"SH"/"SZ"
        :return: API 返回值
        """
        return self.executor.cancel(orig_cl_seq_no, market)
