# -*- coding: utf-8 -*-
"""
OesClientSpi
"""

from typing import Any, Optional
from abc import abstractmethod

from vendor.trade_api.model import (
    # spk_util.py
    SMsgHeadT, OesAsyncApiChannelT,

    # oes_base_constants.py
    eOesBusinessTypeT,
    eOesFundTrsfDirectT,
    eOesTrdSessTypeT,

    # oes_base_model_credit.py
    OesCrdDebtContractReportT,
    OesCrdDebtJournalReportT,
    OesCrdCreditAssetItemT,
    OesCrdDebtContractItemT,
    OesCrdDebtJournalItemT,
    OesCrdExcessStockItemT,
    OesCrdSecurityDebtStatsItemT,
    OesCrdUnderlyingInfoItemT,

    # oes_base_model_option_.py
    OesOptionItemT,
    OesOptHoldingReportT,
    OesOptSettlementConfirmReportT,
    OesOptUnderlyingHoldingReportT,
    OesOptExerciseAssignItemT,
    OesOptUnderlyingHoldingItemT,

    # oes_base_model.py
    OesOrdCnfmT,
    OesOrdRejectT,
    OesTrdCnfmT,
    OesStkHoldingReportT,
    OesCashAssetReportT,
    OesCrdCashRepayReportT,
    OesFundTrsfRejectT,
    OesFundTrsfReportT,
    OesOrdItemT, OesTrdItemT, OesStkHoldingItemT,
    OesCashAssetItemT, OesEtfItemT, OesFundTransferSerialItemT,
    OesStockItemT, OesIssueItemT, OesLotWinningItemT,
    OesCommissionRateItemT, OesCrdCashRepayItemT,

    # oes_qry_packets.py
    OesCustItemT,
    OesInvAcctItemT,
    OesMarketStateItemT,
    OesEtfComponentItemT,
    OesCrdInterestRateItemT,
    OesQryCursorT,

    # oes_qry_packets_credit.py
    OesCrdCashPositionItemT, OesCrdSecurityPositionItemT,

    # oes_qry_packets_option.py
    OesOptHoldingItemT, OesOptPositionLimitItemT, OesOptPurchaseLimitItemT,

    # oes_packets.py
    eOesMsgTypeT, OesRptMsgHeadT, OesRspMsgBodyT,
    OesNotifyInfoReportT, OesChangePasswordRspT,
    OesReportSynchronizationRspT, OesTestRequestRspT,
    OesOptSettlementConfirmRspT, OesNotifyInfoItemT,
)


class OesClientSpi:
    """
    交易接口响应基类
    """

    def __init__(self):
        # @note 解决与oes_api.py互相引用的问题, 故在此导入
        from vendor.trade_api.oes_api import OesClientApi

        self.oes_api: Optional[OesClientApi] = None

    @abstractmethod
    def on_rpt_connect(self,
            channel: OesAsyncApiChannelT,
            user_info: Any) -> int:
        """
        回报通道连接成功的回调函数.

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            user_info (Any, None]): [用户回调参数]

        Returns:
            int: [
                    >0 大于0, 表示需要继续执行默认的 OnConnect 回调处理
                    =0 等于0, 表示已经处理成功
                    <0 小于0, 异步线程将中止运行
                 ]
        """
        return 0

    @abstractmethod
    def on_rpt_connect_failed(self,
            channel: OesAsyncApiChannelT,
            user_info: Any) -> int:
        """
        回报通道连接失败后的回调函数
        - OnConnectFailed 和 OnDisconnect 回调函数的区别在于:
          - 在连接成功以前:
            - 当尝试建立或重建连接时, 如果连接失败则回调 OnConnectFailed;
            - 如果连接成功, 则回调 OnConnect;
          - 在连接成功以后:
            - 如果发生连接中断, 则回调 OnDisconnect.

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            user_info (Any, None]): [用户回调参数]

        Returns:
            int: [
                    >=0 大于等于0, 异步线程将尝试重建连接并继续执行
                    <0  小于0, 异步线程将中止运行
                 ]
        """

        return 0

    @abstractmethod
    def on_rpt_disconnect(self,
            channel: OesAsyncApiChannelT,
            user_info: Any) -> int:
        """
        回报通道连接断开的回调函数，断开会自动重连，这里可以什么都不做

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            user_info (Any, None]): [用户回调参数]
        """
        return 0

    @abstractmethod
    def on_ord_connect(self,
            channel: OesAsyncApiChannelT,
            user_info: Any) -> int:
        """
        委托通道连接成功的回调函数

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            user_info (Any, None]): [用户回调参数]

        Returns:
            int: [
                    >0 大于0, 表示需要继续执行默认的 OnConnect 回调处理
                    =0 等于0, 表示已经处理成功
                    <0 小于0, 异步线程将中止运行
                 ]
        """
        return 0

    @abstractmethod
    def on_ord_connect_failed(self,
            channel: OesAsyncApiChannelT,
            user_info: Any) -> int:
        """
        委托通道连接失败后的回调函数
        - OnConnectFailed 和 OnDisconnect 回调函数的区别在于:
          - 在连接成功以前:
            - 当尝试建立或重建连接时, 如果连接失败则回调 OnConnectFailed;
            - 如果连接成功, 则回调 OnConnect;
          - 在连接成功以后:
            - 如果发生连接中断, 则回调 OnDisconnect.

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            user_info (Any, None]): [用户回调参数]

        Returns:
            int: [
                    >=0 大于等于0, 异步线程将尝试重建连接并继续执行
                    <0  小于0, 异步线程将中止运行
                 ]
        """

        return 0

    @abstractmethod
    def on_ord_disconnect(self,
            channel: OesAsyncApiChannelT,
            user_info: Any) -> int:
        """
        委托通道连接断开的回调函数，断开会自动重连，这里可以什么都不做

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            user_info (Any, None]): [用户回调参数]
        """
        return 0


    # ===================================================================
    # OES回报通道对应的回调函数
    # ===================================================================

    @abstractmethod
    def on_order_insert(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            rpt_msg_head: OesRptMsgHeadT,
            rpt_msg_body: OesOrdCnfmT,
            user_info: Any) -> int:
        """
        接收到OES委托已生成回报后的回调函数 (已通过OES风控检查)

        Args:
            channel (OesAsyncApiChannelT): [消息来源通道]
            msg_head (OesRptMsgHeadT): [通用消息头]
            rpt_msg_head (OesRptMsgHeadT): [回报消息的消息头]
            rpt_msg_body (OesOrdCnfmT): [回报消息的消息体]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0, 成功; <0, 处理失败, 将尝试断开并重建连接]
        """
        return 0

    @abstractmethod
    def on_order_reject(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            rpt_msg_head: OesRptMsgHeadT,
            rpt_msg_body: OesOrdRejectT,
            user_info: Any) -> int:
        """
        接收到OES业务拒绝回报后的回调函数 (未通过OES风控检查等)

        Args:
            channel (OesAsyncApiChannelT): [消息来源通道]
            msg_head (OesRptMsgHeadT): [通用消息头]
            rpt_msg_head (OesRptMsgHeadT): [回报消息的消息头]
            rpt_msg_body (OesOrdRejectT): [回报消息的消息体]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0, 成功; <0, 处理失败, 将尝试断开并重建连接]
        """
        return 0

    @abstractmethod
    def on_order_report(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            rpt_msg_head: OesRptMsgHeadT,
            rpt_msg_body: OesOrdCnfmT,
            user_info: Any) -> int:
        """
        接收到交易所委托回报后的回调函数 (包括交易所委托拒绝、委托确认和撤单完成通知)

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            rpt_msg_head (OesRptMsgHeadT): [回报消息的消息头]
            rpt_msg_body (OesOrdCnfmT): [回报消息的消息体]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0, 成功; <0, 处理失败, 将尝试断开并重建连接]
        """
        return 0

    @abstractmethod
    def on_trade_report(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            rpt_msg_head: OesRptMsgHeadT,
            rpt_msg_body: OesTrdCnfmT,
            user_info: Any) -> int:
        """
        接收到交易所成交回报后的回调函数

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            rpt_msg_head (OesRptMsgHeadT): [回报消息的消息头]
            rpt_msg_body (OesTrdCnfmT): [回报消息的消息体]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0, 成功; <0, 处理失败, 将尝试断开并重建连接]
        """
        return 0

    @abstractmethod
    def on_cash_asset_variation(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            rpt_msg_head: OesRptMsgHeadT,
            rpt_msg_body: OesCashAssetReportT,
            user_info: Any) -> int:
        """
        接收到资金变动信息后的回调函数

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            rpt_msg_head (OesRptMsgHeadT): [回报消息的消息头]
            rpt_msg_body (OesCashAssetReportT): [回报消息的消息体]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0, 成功; <0, 处理失败, 将尝试断开并重建连接]
        """
        return 0

    @abstractmethod
    def on_stock_holding_variation(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            rpt_msg_head: OesRptMsgHeadT,
            rpt_msg_body: OesStkHoldingReportT,
            user_info: Any) -> int:
        """
        接收到股票持仓变动信息后的回调函数

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            rpt_msg_head (OesRptMsgHeadT): [回报消息的消息头]
            rpt_msg_body (OesStkHoldingReportT): [回报消息的消息体]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0, 成功; <0, 处理失败, 将尝试断开并重建连接]
        """
        return 0

    @abstractmethod
    def on_option_holding_variation(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            rpt_msg_head: OesRptMsgHeadT,
            rpt_msg_body: OesOptHoldingReportT,
            user_info: Any) -> int:
        """
        接收到期权持仓变动信息后的回调函数 (仅适用于期权业务)

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            rpt_msg_head (OesRptMsgHeadT): [回报消息的消息头]
            rpt_msg_body (OesOptHoldingReportT): [回报消息的消息体]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0, 成功; <0, 处理失败, 将尝试断开并重建连接]
        """
        return 0

    @abstractmethod
    def on_option_underlying_holding_variation(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            rpt_msg_head: OesRptMsgHeadT,
            rpt_msg_body: OesOptUnderlyingHoldingReportT,
            user_info: Any) -> int:
        """
        接收到期权标的持仓变动信息后的回调函数 (仅适用于期权业务)

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            rpt_msg_head (OesRptMsgHeadT): [回报消息的消息头]
            rpt_msg_body (OesOptUnderlyingHoldingReportT): [回报消息的消息体]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0, 成功; <0, 处理失败, 将尝试断开并重建连接]
        """
        return 0

    @abstractmethod
    def on_option_settlement_confirmed_rpt(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            rpt_msg_head: OesRptMsgHeadT,
            rpt_msg_body: OesOptSettlementConfirmReportT,
            user_info: Any) -> int:
        """
        接收到期权结算单确认回报后的回调函数 (仅适用于期权业务)

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            rpt_msg_head (OesRptMsgHeadT): [回报消息的消息头]
            rpt_msg_body (OesOptSettlementConfirmReportT): [回报消息的消息体]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0, 成功; <0, 处理失败, 将尝试断开并重建连接]
        """
        return 0

    @abstractmethod
    def on_fund_trsf_reject(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            rpt_msg_head: OesRptMsgHeadT,
            rpt_msg_body: OesFundTrsfRejectT,
            user_info: Any) -> int:
        """
        接收到出入金业务拒绝回报后的回调函数

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            rpt_msg_head (OesRptMsgHeadT): [回报消息的消息头]
            rpt_msg_body (OesFundTrsfRejectT): [回报消息的消息体]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0, 成功; <0, 处理失败, 将尝试断开并重建连接]
        """
        return 0

    @abstractmethod
    def on_fund_trsf_report(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            rpt_msg_head: OesRptMsgHeadT,
            rpt_msg_body: OesFundTrsfReportT,
            user_info: Any) -> int:
        """
        接收到出入金委托执行报告后的回调函数

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            rpt_msg_head (OesRptMsgHeadT): [回报消息的消息头]
            rpt_msg_body (OesFundTrsfReportT): [回报消息的消息体]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0, 成功; <0, 处理失败, 将尝试断开并重建连接]
        """
        return 0

    @abstractmethod
    def on_credit_cash_repay_report(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            rpt_msg_head: OesRptMsgHeadT,
            rpt_msg_body: OesCrdCashRepayReportT,
            user_info: Any) -> int:
        """
        接收到融资融券直接还款委托执行报告后的回调函数

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            rpt_msg_head (OesRptMsgHeadT): [回报消息的消息头]
            rpt_msg_body (OesCrdCashRepayReportT): [回报消息的消息体]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0, 成功; <0, 处理失败, 将尝试断开并重建连接]
        """
        return 0

    @abstractmethod
    def on_credit_debt_contract_variation(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            rpt_msg_head: OesRptMsgHeadT,
            rpt_msg_body: OesCrdDebtContractReportT,
            user_info: Any) -> int:
        """
        接收到融资融券合约变动信息后的回调函数

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            rpt_msg_head (OesRptMsgHeadT): [回报消息的消息头]
            rpt_msg_body (OesCrdDebtContractReportT): [回报消息的消息体]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0, 成功; <0, 处理失败, 将尝试断开并重建连接]
        """
        return 0

    @abstractmethod
    def on_credit_debt_journal_report(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            rpt_msg_head: OesRptMsgHeadT,
            rpt_msg_body: OesCrdDebtJournalReportT,
            user_info: Any) -> int:
        """
        接收到融资融券合约流水信息后的回调函数

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            rpt_msg_head (OesRptMsgHeadT): [回报消息的消息头]
            rpt_msg_body (OesCrdDebtJournalReportT): [回报消息的消息体]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0, 成功; <0, 处理失败, 将尝试断开并重建连接]
        """
        return 0

    @abstractmethod
    def on_report_synchronization(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            rpt_msg_head: OesRptMsgHeadT,
            rpt_msg_body: OesReportSynchronizationRspT,
            user_info: Any) -> int:
        """
        接收到回报同步的应答消息后的回调函数

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            rpt_msg_head (OesRptMsgHeadT): [回报消息的消息头]
            rpt_msg_body (OesReportSynchronizationRspT): [回报消息的消息体]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0, 成功; <0, 处理失败, 将尝试断开并重建连接]
        """
        return 0

    @abstractmethod
    def on_market_state(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            rpt_msg_head: OesRptMsgHeadT,
            rpt_msg_body: OesMarketStateItemT,
            user_info: Any) -> int:
        """
        接收到市场状态信息后的回调函数

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            rpt_msg_head (OesRptMsgHeadT): [回报消息的消息头]
            rpt_msg_body (OesMarketStateItemT): [回报消息的消息体]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0, 成功; <0, 处理失败, 将尝试断开并重建连接]
        """
        return 0

    @abstractmethod
    def on_notify_report(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            rpt_msg_head: OesRptMsgHeadT,
            rpt_msg_body: OesNotifyInfoReportT,
            user_info: Any) -> int:
        """
        接收到通知消息后的回调函数

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            rpt_msg_head (OesRptMsgHeadT): [回报消息的消息头]
            rpt_msg_body (OesNotifyInfoReportT): [回报消息的消息体]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0, 成功; <0, 处理失败, 将尝试断开并重建连接]
        """
        return 0

    @abstractmethod
    def on_test_request_rsp(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: OesTestRequestRspT,
            user_info: Any) -> int:
        """
        测试请求应答报文的回调函数

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (SMsgHeadT): [回报消息的消息头]
            msg_body (OesTestRequestRspT): [测试请求的应答报文]
            user_info (Any): [用户回调参数]
        """
        return 0

    @abstractmethod
    def on_heart_beat(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: Any,
            user_info: Any) -> int:
        """
        心跳应答报文的回调函数

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (SMsgHeadT): [回报消息的消息头]
            msg_body (Any, None): [心跳的应答报文]
            user_info (Any): [用户回调参数]
        """

        return 0
    # -------------------------


    # ===================================================================
    # OES密码修改应答对应的回调函数
    # ===================================================================

    @abstractmethod
    def on_change_password_rsp(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: OesChangePasswordRspT,
            user_info: Any) -> int:
        """
        密码修改应答的回调函数

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            - 当前回调函数暂未启用
            msg_body (OesChangePasswordRspT): [回报消息的消息体]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0, 成功; <0, 处理失败, 将尝试断开并重建连接]
        """
        return 0
    # -------------------------


    # ===================================================================
    # 期权结算单确认应答对应的回调函数
    # ===================================================================

    @abstractmethod
    def on_option_confirm_settlement_rsp(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: OesOptSettlementConfirmRspT,
            user_info: Any) -> int:
        """
        期权结算单确认应答的回调函数

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            - 当前回调函数暂未启用
            msg_body (OesOptSettlementConfirmRspT): [回报消息的消息体]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0, 成功; <0, 处理失败, 将尝试断开并重建连接]
        """
        return 0
    # -------------------------


    # ===================================================================
    # OES查询接口对应的回调函数
    # ===================================================================

    @abstractmethod
    def on_query_order(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: OesOrdItemT,
            cursor: OesQryCursorT,
            user_info: Any) -> int:
        """
        查询委托信息的回调函数

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            - 当前回调函数暂未启用
            msg_body (OesOrdItemT): [查询应答的数据条目]
            cursor (OesQryCursorT): [指示查询进度的游标]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """
        return 0

    @abstractmethod
    def on_query_trade(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: OesTrdItemT,
            cursor: OesQryCursorT,
            user_info: Any) -> int:
        """
        查询成交信息的回调函数

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            - 当前回调函数暂未启用
            msg_body (OesTrdItemT): [查询应答的数据条目]
            cursor (OesQryCursorT): [指示查询进度的游标]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """
        return 0

    @abstractmethod
    def on_query_cash_asset(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: OesCashAssetItemT,
            cursor: OesQryCursorT,
            user_info: Any) -> int:
        """
        查询资金信息的回调函数

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            - 当前回调函数暂未启用
            msg_body (OesCashAssetItemT): [查询应答的数据条目]
            cursor (OesQryCursorT): [指示查询进度的游标]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """
        return 0

    @abstractmethod
    def on_query_stk_holding(
            self, channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: OesStkHoldingItemT,
            cursor: OesQryCursorT,
            user_info: Any) -> int:
        """
        查询股票持仓信息的回调函数

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            - 当前回调函数暂未启用
            msg_body (OesStkHoldingItemT): [查询应答的数据条目]
            cursor (OesQryCursorT): [指示查询进度的游标]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """
        return 0

    @abstractmethod
    def on_query_lot_winning(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: OesLotWinningItemT,
            cursor: OesQryCursorT,
            user_info: Any) -> int:
        """
        查询配号/中签信息的回调函数

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            - 当前回调函数暂未启用
            msg_body (OesLotWinningItemT): [查询应答的数据条目]
            cursor (OesQryCursorT): [指示查询进度的游标]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """
        return 0

    @abstractmethod
    def on_query_cust_info(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: OesCustItemT,
            cursor: OesQryCursorT,
            user_info: Any) -> int:
        """
        查询客户信息的回调函数

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            - 当前回调函数暂未启用
            msg_body (OesCustItemT): [查询应答的数据条目]
            cursor (OesQryCursorT): [指示查询进度的游标]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """
        return 0

    @abstractmethod
    def on_query_inv_acct(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: OesInvAcctItemT,
            cursor: OesQryCursorT,
            user_info: Any) -> int:
        """
        查询股东账户信息的回调函数

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            - 当前回调函数暂未启用
            msg_body (OesInvAcctItemT): [查询应答的数据条目]
            cursor (OesQryCursorT): [指示查询进度的游标]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """
        return 0

    @abstractmethod
    def on_query_commission_rate(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: OesCommissionRateItemT,
            cursor: OesQryCursorT,
            user_info: Any) -> int:
        """
        查询佣金信息的回调函数

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            - 当前回调函数暂未启用
            msg_body (OesCommissionRateItemT): [查询应答的数据条目]
            cursor (OesQryCursorT): [指示查询进度的游标]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """
        return 0

    @abstractmethod
    def on_query_fund_transfer_serial(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: OesFundTransferSerialItemT,
            cursor: OesQryCursorT,
            user_info: Any) -> int:
        """
        查询出入金流水的回调函数

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            - 当前回调函数暂未启用
            msg_body (OesFundTransferSerialItemT): [查询应答的数据条目]
            cursor (OesQryCursorT): [指示查询进度的游标]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """
        return 0

    @abstractmethod
    def on_query_issue(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: OesIssueItemT,
            cursor: OesQryCursorT,
            user_info: Any) -> int:
        """
        查询证券发行信息的回调函数

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            - 当前回调函数暂未启用
            msg_body (OesIssueItemT): [查询应答的数据条目]
            cursor (OesQryCursorT): [指示查询进度的游标]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """
        return 0

    @abstractmethod
    def on_query_stock(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: OesStockItemT,
            cursor: OesQryCursorT,
            user_info: Any) -> int:
        """
        查询证券信息的回调函数

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            - 当前回调函数暂未启用
            msg_body (OesStockItemT): [查询应答的数据条目]
            cursor (OesQryCursorT): [指示查询进度的游标]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """
        return 0

    @abstractmethod
    def on_query_etf(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: OesEtfItemT,
            cursor: OesQryCursorT,
            user_info: Any) -> int:
        """
        查询ETF产品信息的回调函数

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            - 当前回调函数暂未启用
            msg_body (OesEtfItemT): [查询应答的数据条目]
            cursor (OesQryCursorT): [指示查询进度的游标]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """
        return 0

    @abstractmethod
    def on_query_etf_component(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: OesEtfComponentItemT,
            cursor: OesQryCursorT,
            user_info: Any) -> int:
        """
        查询ETF成份证券信息的回调函数

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            - 当前回调函数暂未启用
            msg_body (OesEtfComponentItemT): [查询应答的数据条目]
            cursor (OesQryCursorT): [指示查询进度的游标]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """
        return 0

    @abstractmethod
    def on_query_market_state(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: OesMarketStateItemT,
            cursor: OesQryCursorT,
            user_info: Any) -> int:
        """
        查询市场状态信息的回调函数

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            - 当前回调函数暂未启用
            msg_body (OesMarketStateItemT): [查询应答的数据条目]
            cursor (OesQryCursorT): [指示查询进度的游标]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """
        return 0

    @abstractmethod
    def on_query_notify_info(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: OesNotifyInfoItemT,
            cursor: OesQryCursorT,
            user_info: Any) -> int:
        """
        查询通知消息的回调函数

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            - 当前回调函数暂未启用
            msg_body (OesNotifyInfoItemT): [查询应答的数据条目]
            cursor (OesQryCursorT): [指示查询进度的游标]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """
        return 0

    @abstractmethod
    def on_query_option(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: OesOptionItemT,
            cursor: OesQryCursorT,
            user_info: Any) -> int:
        """
        查询期权产品信息的回调函数 (仅适用于期权业务)

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            - 当前回调函数暂未启用
            msg_body (OesOptionItemT): [查询应答的数据条目]
            cursor (OesQryCursorT): [指示查询进度的游标]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """
        return 0

    @abstractmethod
    def on_query_opt_holding(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: OesOptHoldingItemT,
            cursor: OesQryCursorT,
            user_info: Any) -> int:
        """
        查询期权持仓信息的回调函数 (仅适用于期权业务)

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            - 当前回调函数暂未启用
            msg_body (OesOptHoldingItemT): [查询应答的数据条目]
            cursor (OesQryCursorT): [指示查询进度的游标]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """
        return 0

    @abstractmethod
    def on_query_opt_underlying_holding(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: OesOptUnderlyingHoldingItemT,
            cursor: OesQryCursorT,
            user_info: Any) -> int:
        """
        查询期权标的持仓信息的回调函数 (仅适用于期权业务)

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            - 当前回调函数暂未启用
            msg_body (OesOptUnderlyingHoldingItemT): [查询应答的数据条目]
            cursor (OesQryCursorT): [指示查询进度的游标]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """
        return 0

    @abstractmethod
    def on_query_opt_position_limit(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: OesOptPositionLimitItemT,
            cursor: OesQryCursorT,
            user_info: Any) -> int:
        """
        查询期权限仓额度信息的回调函数 (仅适用于期权业务)

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            - 当前回调函数暂未启用
            msg_body (OesOptPositionLimitItemT): [查询应答的数据条目]
            cursor (OesQryCursorT): [指示查询进度的游标]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """
        return 0

    @abstractmethod
    def on_query_opt_purchase_limit(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: OesOptPurchaseLimitItemT,
            cursor: OesQryCursorT,
            user_info: Any) -> int:
        """
        查询期权限购额度信息的回调函数

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            - 当前回调函数暂未启用
            msg_body (OesOptPurchaseLimitItemT): [查询应答的数据条目]
            cursor (OesQryCursorT): [指示查询进度的游标]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """
        return 0

    @abstractmethod
    def on_query_opt_exercise_assign(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: OesOptExerciseAssignItemT,
            cursor: OesQryCursorT,
            user_info: Any) -> int:
        """
        查询期权行权指派信息的回调函数 (仅适用于期权业务)

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            - 当前回调函数暂未启用
            msg_body (OesOptExerciseAssignItemT): [查询应答的数据条目]
            cursor (OesQryCursorT): [指示查询进度的游标]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """
        return 0

    @abstractmethod
    def on_query_crd_debt_contract(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: OesCrdDebtContractItemT,
            cursor: OesQryCursorT,
            user_info: Any) -> int:
        """
        查询融资融券合约信息的回调函数 (仅适用于信用业务)

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            - 当前回调函数暂未启用
            msg_body (OesCrdDebtContractItemT): [查询应答的数据条目]
            cursor (OesQryCursorT): [指示查询进度的游标]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """
        return 0

    @abstractmethod
    def on_query_crd_security_debt_stats(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: OesCrdSecurityDebtStatsItemT,
            cursor: OesQryCursorT,
            user_info: Any) -> int:
        """
        查询融资融券客户单证券负债统计信息的回调函数 (仅适用于信用业务)

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            - 当前回调函数暂未启用
            msg_body (OesCrdSecurityDebtStatsItemT): [查询应答的数据条目]
            cursor (OesQryCursorT): [指示查询进度的游标]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """
        return 0

    @abstractmethod
    def on_query_crd_credit_asset(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: OesCrdCreditAssetItemT,
            cursor: OesQryCursorT,
            user_info: Any) -> int:
        """
        查询信用资产信息的回调函数 (仅适用于信用业务)

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            - 当前回调函数暂未启用
            msg_body (OesCrdCreditAssetItemT): [查询应答的数据条目]
            cursor (OesQryCursorT): [指示查询进度的游标]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """
        return 0

    @abstractmethod
    def on_query_crd_cash_repay_order(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: OesCrdCashRepayItemT,
            cursor: OesQryCursorT,
            user_info: Any) -> int:
        """
        查询融资融券直接还款委托信息的回调函数 (仅适用于信用业务)

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            - 当前回调函数暂未启用
            msg_body (OesCrdCashRepayItemT): [查询应答的数据条目]
            cursor (OesQryCursorT): [指示查询进度的游标]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """
        return 0

    @abstractmethod
    def on_query_crd_cash_position(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: OesCrdCashPositionItemT,
            cursor: OesQryCursorT,
            user_info: Any) -> int:
        """
        查询融资融券资金头寸信息的回调函数 (仅适用于信用业务)

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            - 当前回调函数暂未启用
            msg_body (OesCrdCashPositionItemT): [查询应答的数据条目]
            cursor (OesQryCursorT): [指示查询进度的游标]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """
        return 0

    @abstractmethod
    def on_query_crd_security_position(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: OesCrdSecurityPositionItemT,
            cursor: OesQryCursorT,
            user_info: Any) -> int:
        """
        查询查询融资融券证券头寸信息的回调函数 (仅适用于信用业务)

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            - 当前回调函数暂未启用
            msg_body (OesCrdSecurityPositionItemT): [查询应答的数据条目]
            cursor (OesQryCursorT): [指示查询进度的游标]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """
        return 0

    @abstractmethod
    def on_query_crd_holding(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: OesStkHoldingItemT,
            cursor: OesQryCursorT,
            user_info: Any) -> int:
        """
        查询信用持仓信息的回调函数

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            - 当前回调函数暂未启用
            msg_body (OesStkHoldingItemT): [查询应答的数据条目]
            cursor (OesQryCursorT): [指示查询进度的游标]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """
        return 0

    @abstractmethod
    def on_query_crd_excess_stock(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: OesCrdExcessStockItemT,
            cursor: OesQryCursorT,
            user_info: Any) -> int:
        """
        查询融资融券余券信息的回调函数 (仅适用于信用业务)

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            - 当前回调函数暂未启用
            msg_body (OesCrdExcessStockItemT): [查询应答的数据条目]
            cursor (OesQryCursorT): [指示查询进度的游标]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """
        return 0

    @abstractmethod
    def on_query_crd_debt_journal(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: OesCrdDebtJournalItemT,
            cursor: OesQryCursorT,
            user_info: Any) -> int:
        """
        查询融资融券合约流水信息的回调函数 (仅适用于信用业务)

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            - 当前回调函数暂未启用
            msg_body (OesCrdDebtJournalItemT): [查询应答的数据条目]
            cursor (OesQryCursorT): [指示查询进度的游标]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """
        return 0

    @abstractmethod
    def on_query_crd_interest_rate(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: OesCrdInterestRateItemT,
            cursor: OesQryCursorT,
            user_info: Any) -> int:
        """
        查询融资融券息费利率信息的回调函数 (仅适用于信用业务)

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            - 当前回调函数暂未启用
            msg_body (OesCrdInterestRateItemT): [查询应答的数据条目]
            cursor (OesQryCursorT): [指示查询进度的游标]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """
        return 0

    @abstractmethod
    def on_query_crd_underlying_info(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: OesCrdUnderlyingInfoItemT,
            cursor: OesQryCursorT,
            user_info: Any) -> int:
        """
        查询融资融券可充抵保证金证券及融资融券标的信息的回调函数 (仅适用于信用业务)

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            - 当前回调函数暂未启用
            msg_body (OesCrdUnderlyingInfoItemT): [查询应答的数据条目]
            cursor (OesQryCursorT): [指示查询进度的游标]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """
        return 0
