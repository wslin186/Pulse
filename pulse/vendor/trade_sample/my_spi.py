"""
OES SPI回调函数类
"""
from typing import Any

from vendor.trade_api import (
    # spk_util.py
    SMsgHeadT, OesAsyncApiChannelT,

    # oes_base_constants.py
    eOesBusinessTypeT,
    eOesFundTrsfDirectT,
    eOesTrdSessTypeT,
    eOesNotifyTypeT,
    eOesNotifyScopeT,

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

    # oes_spi_lite.py
    OesClientSpi
)


class OesClientMySpi(OesClientSpi):
    """
    OES-SPI回调函数类
    """

    def __init__(self):
        super().__init__()

        # 自定义属性
        self.something: Any = None

    def __sample_subscribe_on_connect(
            self, channel: OesAsyncApiChannelT,
            user_info: Any) -> int:
        """
        连接完成后, 交易回报通道订阅的样例展示 (仅供参考)

        Args:
            channel (OesAsyncApiChannelT): [回报通道]
            user_info (Any, None): [用户回调参数]
        """
        # @note 提示:
        # - 只是出于演示的目的才如此处理, 实盘程序根据需要自行实现
        if user_info == "subscribe_nothing_on_connect":
            # 连接完成后, 不订阅任何回报数据
            return self.oes_api.subscribe_nothing_on_connect(channel)

        elif user_info == "subscribe_by_cfg":
            # 连接完成后, 根据配置文件中的参数, 订阅回报数据
            return self.oes_api.default_on_connect(channel)

        else:
            # 默认连接完成后, 根据配置文件中的参数, 订阅行情数据
            return 1

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

        tag: str = channel.pChannelCfg.contents.channelTag.decode()

        print(f">>> 回报通道: {tag} 连接成功! "
              f"业务类型: {self.oes_api.get_business_type(channel)}")
        return self.__sample_subscribe_on_connect(channel, user_info)

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
        tag: str = channel.pChannelCfg.contents.channelTag.decode()

        print(f">>> 回报通道: {tag} 连接失败! "
              f"业务类型: {self.oes_api.get_business_type(channel)}")
        return 0

    def on_rpt_disconnect(self,
            channel: OesAsyncApiChannelT,
            user_info: Any) -> int:
        """
        回报通道连接断开的回调函数，断开会自动重连，这里可以什么都不做

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            user_info (Any, None]): [用户回调参数]
        """
        tag: str = channel.pChannelCfg.contents.channelTag.decode()

        print(f">>> 回报通道: {tag} 连接断开! "
              f"业务类型: {self.oes_api.get_business_type(channel)}")
        return 0

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
        tag: str = channel.pChannelCfg.contents.channelTag.decode()

        print(f">>> 委托通道: {tag} 连接成功! "
              f"业务类型: {self.oes_api.get_business_type(channel)}")
        return 0

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
        tag: str = channel.pChannelCfg.contents.channelTag.decode()

        print(f">>> 委托通道: {tag} 连接失败! "
              f"业务类型: {self.oes_api.get_business_type(channel)}")
        return 0

    def on_ord_disconnect(self,
            channel: OesAsyncApiChannelT,
            user_info: Any) -> int:
        """
        委托通道连接断开的回调函数，断开会自动重连，这里可以什么都不做

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            user_info (Any, None]): [用户回调参数]
        """
        tag: str = channel.pChannelCfg.contents.channelTag.decode()

        print(f">>> 委托通道: {tag} 连接断开! "
              f"业务类型: {self.oes_api.get_business_type(channel)}")
        return 0


    # ===================================================================
    # OES回报通道对应的回调函数
    # ===================================================================

    def on_order_insert(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            rpt_msg_head: OesRptMsgHeadT,
            rpt_msg_body: OesOrdCnfmT,
            user_info: Any) -> int:
        """
        接收到OES委托已生成回报后的回调函数 (已通过OES风控检查)

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            rpt_msg_head (OesRptMsgHeadT): [回报消息的消息头]
            rpt_msg_body (OesOrdCnfmT): [委托回报数据]
            user_info (Any, None): [用户回调参数]

        Returns:
            [int]: [>=0, 成功; <0, 处理失败, 将尝试断开并重建连接]
        """
        channel_tag: str = channel.pChannelCfg.contents.channelTag.decode()

        print(f">>> 收到委托已收回报: "
            f"通道[{channel_tag}], "
            f"执行类型[{rpt_msg_head.execType}], "
            f"客户端环境号[{rpt_msg_body.clEnvId}], "
            f"客户委托流水号[{rpt_msg_body.clSeqNo}], "
            f"会员内部编号[{rpt_msg_body.clOrdId}], "
            f"证券账户[{rpt_msg_body.invAcctId.decode()}], "
            f"证券代码[{rpt_msg_body.securityId.decode()}], "
            f"市场代码[{rpt_msg_body.mktId}], "
            f"订单类型[{rpt_msg_body.ordType}], "
            f"买卖类型[{rpt_msg_body.bsType}], "
            f"委托状态[{rpt_msg_body.ordStatus}], "
            f"委托日期[{rpt_msg_body.ordDate}], "
            f"委托接收时间[{rpt_msg_body.ordTime}], "
            f"委托确认时间[{rpt_msg_body.ordCnfmTime}], "
            f"委托数量[{rpt_msg_body.ordQty}], "
            f"委托价格[{rpt_msg_body.ordPrice}], "
            f"撤单数量[{rpt_msg_body.canceledQty}], "
            f"累计成交份数[{rpt_msg_body.cumQty}], "
            f"累计成交金额[{rpt_msg_body.cumAmt}], "
            f"累计债券利息[{rpt_msg_body.cumInterest}], "
            f"累计交易佣金[{rpt_msg_body.cumFee}], "
            f"冻结交易金额[{rpt_msg_body.frzAmt}], "
            f"冻结债券利息[{rpt_msg_body.frzInterest}], "
            f"冻结交易佣金[{rpt_msg_body.frzFee}], "
            f"当前冻结保证金[{rpt_msg_body.frzMargin}], "
            f"累计冻结保证金[{rpt_msg_body.cumMargin}], "
            f"被撤内部委托编号[{rpt_msg_body.origClOrdId}], "
            f"拒绝原因[{rpt_msg_body.ordRejReason}], "
            f"交易所错误码[{rpt_msg_body.exchErrCode}]")

        return 0

    def on_order_reject(self,
            channel: OesAsyncApiChannelT,
            msg_head: SMsgHeadT,
            rpt_msg_head: OesRptMsgHeadT,
            rpt_msg_body: OesOrdRejectT,
            user_info: Any) -> int:
        """
        接收到OES业务拒绝回报后的回调函数 (未通过OES风控检查等)

        Args:
            channel (OesAsyncApiChannelT): [通道信息]
            msg_head (OesRptMsgHeadT): [通用消息头]
            rpt_msg_head (OesRptMsgHeadT): [回报消息的消息头]
            rpt_msg_body (OesOrdRejectT): [回报消息的消息体]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0, 成功; <0, 处理失败, 将尝试断开并重建连接]
        """
        channel_tag: str = channel.pChannelCfg.contents.channelTag.decode()

        print(f">>> 收到委托业务拒绝回报: "
            f"通道[{channel_tag}], "
            f"执行类型[{rpt_msg_head.execType}], "
            f"客户端环境号[{rpt_msg_body.clEnvId}], "
            f"客户委托流水号[{rpt_msg_body.clSeqNo}], "
            f"证券账户[{rpt_msg_body.invAcctId.decode()}], "
            f"证券代码[{rpt_msg_body.securityId.decode()}], "
            f"市场代码[{rpt_msg_body.mktId}], "
            f"委托类型[{rpt_msg_body.ordType}], "
            f"买卖类型[{rpt_msg_body.bsType}], "
            f"委托数量[{rpt_msg_body.ordQty}], "
            f"委托价格[{rpt_msg_body.ordPrice}], "
            f"原始委托的客户订单编号[{rpt_msg_body.origClOrdId}], "
            f"错误码[{rpt_msg_head.ordRejReason}]")

        return 0

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
        channel_tag: str = channel.pChannelCfg.contents.channelTag.decode()

        print(f">>> 收到委托回报: "
            f"通道[{channel_tag}], "
            f"执行类型[{rpt_msg_head.execType}], "
            f"客户端环境号[{rpt_msg_body.clEnvId}], "
            f"客户委托流水号[{rpt_msg_body.clSeqNo}], "
            f"会员内部编号[{rpt_msg_body.clOrdId}], "
            f"证券账户[{rpt_msg_body.invAcctId.decode()}], "
            f"证券代码[{rpt_msg_body.securityId.decode()}], "
            f"市场代码[{rpt_msg_body.mktId}], "
            f"订单类型[{rpt_msg_body.ordType}], "
            f"买卖类型[{rpt_msg_body.bsType}], "
            f"委托状态[{rpt_msg_body.ordStatus}], "
            f"委托日期[{rpt_msg_body.ordDate}], "
            f"委托接收时间[{rpt_msg_body.ordTime}], "
            f"委托确认时间[{rpt_msg_body.ordCnfmTime}], "
            f"委托数量[{rpt_msg_body.ordQty}], "
            f"委托价格[{rpt_msg_body.ordPrice}], "
            f"撤单数量[{rpt_msg_body.canceledQty}], "
            f"累计成交份数[{rpt_msg_body.cumQty}], "
            f"累计成交金额[{rpt_msg_body.cumAmt}], "
            f"累计债券利息[{rpt_msg_body.cumInterest}], "
            f"累计交易佣金[{rpt_msg_body.cumFee}], "
            f"冻结交易金额[{rpt_msg_body.frzAmt}], "
            f"冻结债券利息[{rpt_msg_body.frzInterest}], "
            f"冻结交易佣金[{rpt_msg_body.frzFee}], "
            f"当前冻结保证金[{rpt_msg_body.frzMargin}], "
            f"累计冻结保证金[{rpt_msg_body.cumMargin}], "
            f"被撤内部委托编号[{rpt_msg_body.origClOrdId}], "
            f"拒绝原因[{rpt_msg_body.ordRejReason}], "
            f"交易所错误码[{rpt_msg_body.exchErrCode}]")

        return 0

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
        channel_tag: str = channel.pChannelCfg.contents.channelTag.decode()

        print(f">>> 收到成交回报: "
            f"通道[{channel_tag}], "
            f"执行类型[{rpt_msg_head.execType}], "
            f"成交编号[{rpt_msg_body.exchTrdNum}], "
            f"会员内部编号[{rpt_msg_body.clOrdId}], "
            f"委托客户端环境号[{rpt_msg_body.clEnvId}], "
            f"客户委托流水号[{rpt_msg_body.clSeqNo}], "
            f"证券账户[{rpt_msg_body.invAcctId.decode()}], "
            f"证券代码[{rpt_msg_body.securityId.decode()}], "
            f"市场代码[{rpt_msg_body.mktId}], "
            f"买卖方向[{rpt_msg_body.trdSide}], "
            f"委托买卖类型[{rpt_msg_body.ordBuySellType}], "
            f"证券类型[{rpt_msg_body.securityType}], "
            f"证券子类型[{rpt_msg_body.subSecurityType}], "
            f"成交日期[{rpt_msg_body.trdDate}], "
            f"成交时间[{rpt_msg_body.trdTime}], "
            f"成交数量[{rpt_msg_body.trdQty}], "
            f"成交价格[{rpt_msg_body.trdPrice}], "
            f"成交金额[{rpt_msg_body.trdAmt}], "
            f"债券利息[{rpt_msg_body.trdInterest}], "
            f"交易费用[{rpt_msg_body.trdFee}], "
            f"累计成交数量[{rpt_msg_body.cumQty}], "
            f"累计成交金额[{rpt_msg_body.cumAmt}], "
            f"累计债券利息[{rpt_msg_body.cumInterest}], "
            f"累计交易费用[{rpt_msg_body.cumFee}], "
            f"占用/释放保证金[{rpt_msg_body.trdMargin}], "
            f"累计占用/释放保证金[{rpt_msg_body.cumMargin}], "
            f"PBU代码[{rpt_msg_body.pbuId}]")

        return 0

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
        channel_tag: str = channel.pChannelCfg.contents.channelTag.decode()

        outbuf = ""
        outbuf += f">>> 收到资金变动回报: " \
                  f"通道[{channel_tag}], " \
                  f"资金账户代码[{rpt_msg_body.cashAcctId.decode()}], "
        outbuf += f"客户代码[{rpt_msg_body.custId.decode()}], " \
                  f"币种[{rpt_msg_body.currType}], "
        outbuf += f"资金类型[{rpt_msg_body.cashType}], " \
                  f"资金账户状态[{rpt_msg_body.cashAcctStatus}], "
        outbuf += f"期初余额[{rpt_msg_body.beginningBal}], "
        outbuf += f"期初可用余额[{rpt_msg_body.beginningAvailableBal}], "
        outbuf += f"期初可取余额[{rpt_msg_body.beginningDrawableBal}], "
        outbuf += f"不可用余额[{rpt_msg_body.disableBal}], " \
                  f"累计存入金额[{rpt_msg_body.totalDepositAmt}], "
        outbuf += f"累计提取金额[{rpt_msg_body.totalWithdrawAmt}], "
        outbuf += f"当前提取冻结金额[{rpt_msg_body.withdrawFrzAmt}], "
        outbuf += f"累计卖金额[{rpt_msg_body.totalSellAmt}], " \
                  f"累计买金额[{rpt_msg_body.totalBuyAmt}], "
        outbuf += f"当前买冻结金额[{rpt_msg_body.buyFrzAmt}], " \
                  f"累计费用金额[{rpt_msg_body.totalFeeAmt}], "
        outbuf += f"当前费用冻结金额[{rpt_msg_body.feeFrzAmt}], "
        outbuf += f"累计委托流量费[{rpt_msg_body.ordTrafficFeeAmt}], "
        outbuf += f"当前维持保证金金额[{rpt_msg_body.marginAmt}], "
        outbuf += f"当前保证金冻结金额[{rpt_msg_body.marginFrzAmt}], "
        outbuf += f"内部划拨净发生金额[{rpt_msg_body.totalInternalAllotAmt}], "
        outbuf += f"内部划拨在途金额[{rpt_msg_body.internalAllotUncomeAmt}], "
        outbuf += f"当前余额[{rpt_msg_body.currentTotalBal}], "
        outbuf += f"当前可用余额[{rpt_msg_body.currentAvailableBal}], "
        outbuf += f"当前可取余额[{rpt_msg_body.currentDrawableBal}], "

        if self.oes_api.get_business_type(channel) \
                == eOesBusinessTypeT.OES_BUSINESS_TYPE_OPTION:
            outbuf += f"未对冲实时保证金金额[{rpt_msg_body.optionExt.totalMarketMargin}], "
            outbuf += f"已对冲实时保证金金额[{rpt_msg_body.optionExt.totalNetMargin}]"
        else:
            outbuf = outbuf[:-2]

        print(outbuf)
        return 0

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
        channel_tag: str = channel.pChannelCfg.contents.channelTag.decode()

        print(f">>> 收到股票持仓变动回报: "
            f"通道[{channel_tag}], "
            f"证券账户[{rpt_msg_body.invAcctId.decode()}], "
            f"证券代码[{rpt_msg_body.securityId.decode()}], "
            f"市场代码[{rpt_msg_body.mktId}], "
            f"日初持仓[{rpt_msg_body.originalHld}], "
            f"日初可用持仓[{rpt_msg_body.originalAvlHld}], "
            f"当日可减持额度[{rpt_msg_body.maxReduceQuota}], "
            f"日中累计买入持仓[{rpt_msg_body.totalBuyHld}], "
            f"日中累计卖出持仓[{rpt_msg_body.totalSellHld}], "
            f"当前卖出冻结持仓[{rpt_msg_body.sellFrzHld}], "
            f"手动冻结持仓[{rpt_msg_body.manualFrzHld}], "
            f"日中累计转换获得持仓[{rpt_msg_body.totalTrsfInHld}], "
            f"日中累计转换付出持仓[{rpt_msg_body.totalTrsfOutHld}], "
            f"当前转换付出冻结持仓[{rpt_msg_body.trsfOutFrzHld}], "
            f"日初锁定持仓[{rpt_msg_body.originalLockHld}], "
            f"日中累计锁定持仓[{rpt_msg_body.totalLockHld}], "
            f"日中累计解锁持仓[{rpt_msg_body.totalUnlockHld}], "
            f"日初总持仓成本[{rpt_msg_body.originalCostAmt}], "
            f"当日累计买入金额[{rpt_msg_body.totalBuyAmt}], "
            f"当日累计卖出金额[{rpt_msg_body.totalSellAmt}], "
            f"当日累计买入费用[{rpt_msg_body.totalBuyFee}], "
            f"当日累计卖出费用[{rpt_msg_body.totalSellFee}], "
            f"持仓成本价[{rpt_msg_body.costPrice}], "
            f"当前总持仓[{rpt_msg_body.sumHld}], "
            f"当前可卖持仓[{rpt_msg_body.sellAvlHld}], "
            f"当前可转换付出持仓[{rpt_msg_body.trsfOutAvlHld}], "
            f"当前可锁定持仓[{rpt_msg_body.lockAvlHld}]")

        return 0

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
        channel_tag: str = channel.pChannelCfg.contents.channelTag.decode()

        print(f">>> 收到期权持仓变动回报: "
            f"通道[{channel_tag}], "
            f"证券账户[{rpt_msg_body.invAcctId.decode()}], "
            f"期权合约代码[{rpt_msg_body.securityId.decode()}], "
            f"市场代码[{rpt_msg_body.mktId}], "
            f"持仓类型[{rpt_msg_body.positionType}], "
            f"产品类型[{rpt_msg_body.productType}], "
            f"证券类型[{rpt_msg_body.securityType}], "
            f"证券子类型[{rpt_msg_body.subSecurityType}], "
            f"合约类型[{rpt_msg_body.contractType}], "
            f"套保标志[{rpt_msg_body.hedgeFlag}], "
            f"日初总持仓张数[{rpt_msg_body.originalQty}], "
            f"日初可用持仓[{rpt_msg_body.originalAvlQty}], "
            f"日初总持仓成本[{rpt_msg_body.originalCostAmt}], "
            f"日初总占用金额[{rpt_msg_body.originalCarryingAmt}], "
            f"日中累计开仓张数[{rpt_msg_body.totalOpenQty}], "
            f"开仓委托未成交张数[{rpt_msg_body.uncomeQty}], "
            f"日中累计平仓张数[{rpt_msg_body.totalCloseQty}], "
            f"平仓在途冻结张数[{rpt_msg_body.closeFrzQty}], "
            f"手动冻结张数[{rpt_msg_body.manualFrzQty}], "
            f"日中累计获得权利金[{rpt_msg_body.totalInPremium}], "
            f"日中累计付出权利金[{rpt_msg_body.totalOutPremium}],"
            f"日中累计开仓费用[{rpt_msg_body.totalOpenFee}], "
            f"日中累计平仓费用[{rpt_msg_body.totalCloseFee}], "
            f"权利仓行权冻结张数[{rpt_msg_body.exerciseFrzQty}], "
            f"义务仓持仓保证金[{rpt_msg_body.positionMargin}], "
            f"可平仓张数[{rpt_msg_body.closeAvlQty}], "
            f"可行权张数[{rpt_msg_body.exerciseAvlQty}], "
            f"总持仓张数[{rpt_msg_body.sumQty}], "
            f"持仓成本价[{rpt_msg_body.costPrice}], "
            f"持仓均价[{rpt_msg_body.carryingAvgPrice}], "
            f"可备兑标的券数量[{rpt_msg_body.coveredAvlUnderlyingQty}], "
            f"当前可用的权利仓限额[{rpt_msg_body.availableLongPositionLimit}], "
            f"当前可用的总持仓限额[{rpt_msg_body.availableTotalPositionLimit}], "
            f"当前可用的单日买入开仓限额[{rpt_msg_body.availableDailyBuyOpenLimit}]")

        return 0

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
        channel_tag: str = channel.pChannelCfg.contents.channelTag.decode()

        print(f">>> 收到期权标的持仓变动回报: "
            f"通道[{channel_tag}], "
            f"证券账户[{rpt_msg_body.invAcctId.decode()}], "
            f"标的证券代码[{rpt_msg_body.underlyingSecurityId.decode()}], "
            f"市场代码(衍生品市场)[{rpt_msg_body.mktId}], "
            f"标的市场代码[{rpt_msg_body.underlyingMktId}], "
            f"标的证券类型[{rpt_msg_body.underlyingSecurityType}], "
            f"标的证券子类型[{rpt_msg_body.underlyingSubSecurityType}], "
            f"日初标的证券的总持仓数量 [{rpt_msg_body.originalHld}], "
            f"日初标的证券的可用持仓数量[{rpt_msg_body.originalAvlHld}], "
            f"日初备兑仓实际占用的标的证券数量[{rpt_msg_body.originalCoveredQty}], "
            f"日初备兑仓应占用的标的证券数量[{rpt_msg_body.initialCoveredQty}], "
            f"当前备兑仓实际占用的标的证券数量[{rpt_msg_body.coveredQty}], "
            f"当前备兑仓占用标的证券的缺口数量[{rpt_msg_body.coveredGapQty}], "
            f"当前可用于备兑开仓的标的持仓数量[{rpt_msg_body.coveredAvlQty}], "
            f"当前可锁定的标的持仓数量[{rpt_msg_body.lockAvlQty}], "
            f"总持仓数量[{rpt_msg_body.sumHld}], "
            f"当日最大可减持额度[{rpt_msg_body.maxReduceQuota}]")

        return 0

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
        channel_tag: str = channel.pChannelCfg.contents.channelTag.decode()

        print(f">>> 收到结算单确认回报: "
            f"通道[{channel_tag}], "
            f"客户代码[{rpt_msg_body.custId.decode()}], "
            f"客户端编号[{rpt_msg_body.clientId}], "
            f"客户端环境号[{rpt_msg_body.clEnvId}], "
            f"发生日期[{rpt_msg_body.transDate}], "
            f"发生时间[{rpt_msg_body.transTime}], "
            f"失败原因[{rpt_msg_body.rejReason}]")

        return 0

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
        channel_tag: str = channel.pChannelCfg.contents.channelTag.decode()

        print(f">>> 收到出入金委托拒绝回报: "
            f"通道[{channel_tag}], "
            f"执行类型[{rpt_msg_head.execType}], "
            f"客户端环境号[{rpt_msg_body.clEnvId}], "
            f"出入金流水号[{rpt_msg_body.clSeqNo}], "
            f"资金账户[{rpt_msg_body.cashAcctId.decode()}], "
            f"是否仅调拨[{rpt_msg_body.fundTrsfType}], "
            f"出入金方向[{rpt_msg_body.direct}], "
            f"出入金金额[{rpt_msg_body.occurAmt}], "
            f"错误码[{rpt_msg_body.rejReason}], "
            f"错误信息[{rpt_msg_body.errorInfo.decode()}]")

        return 0

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
        channel_tag: str = channel.pChannelCfg.contents.channelTag.decode()

        print(f">>> 收到出入金委托执行回报: "
            f"通道[{channel_tag}], "
            f"执行类型[{rpt_msg_head.execType}], "
            f"错误原因[{rpt_msg_body.rejReason}], "
            f"主柜错误码[{rpt_msg_body.counterErrCode}], "
            f"错误信息[{rpt_msg_body.errorInfo.decode()}], "
            f"客户端环境号[{rpt_msg_body.clEnvId}], "
            f"出入金流水号[{rpt_msg_body.clSeqNo}], "
            f"出入金编号[{rpt_msg_body.fundTrsfId}], "
            f"资金账户[{rpt_msg_body.cashAcctId.decode()}], "
            f"是否仅调拨[{rpt_msg_body.fundTrsfType}], "
            f"出入金方向[{rpt_msg_body.direct}], "
            f"出入金金额[{rpt_msg_body.occurAmt}], "
            f"出入金状态[{rpt_msg_body.trsfStatus}], "
            f"接收日期[{rpt_msg_body.operDate}], "
            f"接收时间[{rpt_msg_body.operTime}], "
            f"上报时间[{rpt_msg_body.dclrTime}], "
            f"完成时间[{rpt_msg_body.doneTime}]")

        return 0

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
        channel_tag: str = channel.pChannelCfg.contents.channelTag.decode()

        print(f">>> 收到融资融券直接还款委托执行报告: "
            f"通道[{channel_tag}], "
            f"执行类型[{rpt_msg_head.execType}], "
            f"客户委托流水号[{rpt_msg_body.clSeqNo}], "
            f"归还模式[{rpt_msg_body.repayMode}], "
            f"归还指令类型[{rpt_msg_body.repayJournalType}], "
            f"归还金额[{rpt_msg_body.repayAmt}], "
            f"资金账户代码[{rpt_msg_body.cashAcctId.decode()}], "
            f"指定归还的合约编号[{rpt_msg_body.debtId}], "
            f"证券账户[{rpt_msg_body.invAcctId.decode()}], "
            f"证券代码[{rpt_msg_body.securityId.decode()}], "
            f"市场代码[{rpt_msg_body.mktId}], "
            f"委托价格[{rpt_msg_body.ordPrice}], "
            f"归还数量[{rpt_msg_body.ordQty}], "
            f"委托日期[{rpt_msg_body.ordDate}], "
            f"委托时间[{rpt_msg_body.ordTime}], "
            f"客户订单编号[{rpt_msg_body.clOrdId}], "
            f"客户端编号[{rpt_msg_body.clientId}], "
            f"客户端环境号[{rpt_msg_body.clEnvId}], "
            f"委托强制标志[{rpt_msg_body.mandatoryFlag}], "
            f"订单当前状态[{rpt_msg_body.ordStatus}], "
            f"所有者类型[{rpt_msg_body.ownerType}], "
            f"订单拒绝原因[{rpt_msg_body.ordRejReason}], "
            f"实际归还数量[{rpt_msg_body.repaidQty}], "
            f"实际归还金额[{rpt_msg_body.repaidAmt}], "
            f"实际归还费用[{rpt_msg_body.repaidFee}], "
            f"实际归还利息[{rpt_msg_body.repaidInterest}], "
            f"营业部编号[{rpt_msg_body.branchId}]")

        return 0

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
        channel_tag: str = channel.pChannelCfg.contents.channelTag.decode()

        print(f">>> 收到融资融券合约变动消息: "
            f"通道[{channel_tag}], "
            f"合约编号[{rpt_msg_body.debtId}], "
            f"资金账户代码[{rpt_msg_body.cashAcctId.decode()}], "
            f"股东账户代码[{rpt_msg_body.invAcctId.decode()}], "
            f"证券代码[{rpt_msg_body.securityId.decode()}], "
            f"市场代码[{rpt_msg_body.mktId}], "
            f"证券类型[{rpt_msg_body.securityType}], "
            f"证券子类型[{rpt_msg_body.subSecurityType}], "
            f"证券的产品类型[{rpt_msg_body.securityProductType}], "
            f"负债类型[{rpt_msg_body.debtType}], "
            f"负债状态[{rpt_msg_body.debtStatus}], "
            f"期初负债状态[{rpt_msg_body.originalDebtStatus}], "
            f"负债归还模式[{rpt_msg_body.debtRepayMode}], "
            f"委托日期[{rpt_msg_body.ordDate}], "
            f"委托价格[{rpt_msg_body.ordPrice}], "
            f"委托数量[{rpt_msg_body.ordQty}], "
            f"成交数量[{rpt_msg_body.trdQty}], "
            f"委托金额[{rpt_msg_body.ordAmt}], "
            f"成交金额[{rpt_msg_body.trdAmt}], "
            f"成交费用[{rpt_msg_body.trdFee}], "
            f"实时合约金额[{rpt_msg_body.currentDebtAmt}], "
            f"实时合约手续费[{rpt_msg_body.currentDebtFee}], "
            f"实时合约利息[{rpt_msg_body.currentDebtInterest}], "
            f"实时合约数量[{rpt_msg_body.currentDebtQty}], "
            f"在途冻结数量[{rpt_msg_body.uncomeDebtQty}], "
            f"在途冻结金额[{rpt_msg_body.uncomeDebtAmt}], "
            f"在途冻结手续费[{rpt_msg_body.uncomeDebtFee}], "
            f"在途冻结利息[{rpt_msg_body.uncomeDebtInterest}], "
            f"累计已归还金额[{rpt_msg_body.totalRepaidAmt}], "
            f"累计已归还手续费[{rpt_msg_body.totalRepaidFee}], "
            f"累计已归还利息[{rpt_msg_body.totalRepaidInterest}], "
            f"累计已归还数量[{rpt_msg_body.totalRepaidQty}], "
            f"期初待归还金额[{rpt_msg_body.originalDebtAmt}], "
            f"期初待归还手续费[{rpt_msg_body.originalDebtFee}], "
            f"期初待归还利息[{rpt_msg_body.originalDebtInterest}], "
            f"期初待归还数量[{rpt_msg_body.originalDebtQty}], "
            f"期初已归还数量[{rpt_msg_body.originalRepaidQty}], "
            f"期初已归还金额[{rpt_msg_body.originalRepaidAmt}], "
            f"期初已归还利息[{rpt_msg_body.originalRepaidInterest}], "
            f"罚息[{rpt_msg_body.punishInterest}], "
            f"保证金比例[{rpt_msg_body.marginRatio}], "
            f"融资利率/融券费率[{rpt_msg_body.interestRate}], "
            f"负债截止日期[{rpt_msg_body.repayEndDate}], "
            f"头寸编号[{rpt_msg_body.cashGroupNo}], "
            f"展期次数[{rpt_msg_body.postponeTimes}], "
            f"展期状态[{rpt_msg_body.postponeStatus}], "
            f"同一证券所有融券合约的合计待归还负债数量[{rpt_msg_body.securityRepayableDebtQty}], "
            f"该融券合约的当前待归还负债数量[{rpt_msg_body.contractRepayableDebtQty}]")

        return 0

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
        channel_tag: str = channel.pChannelCfg.contents.channelTag.decode()

        print(
            f">>> 收到融资融券合约流水信息: "
            f"通道[{channel_tag}], "
            f"合约编号[{rpt_msg_body.debtId}], "
            f"资金账户代码[{rpt_msg_body.cashAcctId.decode()}], "
            f"股东账户代码[{rpt_msg_body.invAcctId.decode()}], "
            f"证券代码[{rpt_msg_body.securityId.decode()}], "
            f"市场代码[{rpt_msg_body.mktId}], "
            f"负债类型[{rpt_msg_body.debtType}], "
            f"流水类型[{rpt_msg_body.journalType}], "
            f"强制标志[{rpt_msg_body.mandatoryFlag}], "
            f"同一融资融券合约的负债流水顺序号[{rpt_msg_body.seqNo}], "
            f"发生金额[{rpt_msg_body.occurAmt}], "
            f"发生费用[{rpt_msg_body.occurFee}], "
            f"发生利息[{rpt_msg_body.occurInterest}], "
            f"发生证券数量[{rpt_msg_body.occurQty}], "
            f"后余证券数量[{rpt_msg_body.postQty}], "
            f"后余金额[{rpt_msg_body.postAmt}], "
            f"后余费用[{rpt_msg_body.postFee}], "
            f"后余利息[{rpt_msg_body.postInterest}], "
            f"融券合约流水的理论发生金额[{rpt_msg_body.shortSellTheoryOccurAmt}], "
            f"归还息费时使用融券卖出所得抵扣的金额[{rpt_msg_body.useShortSellGainedAmt}], "
            f"委托日期[{rpt_msg_body.ordDate}], "
            f"委托时间[{rpt_msg_body.ordTime}]")

        return 0

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
        channel_tag: str = channel.pChannelCfg.contents.channelTag.decode()

        print(
            f">>> 收到回报同步响应: "
            f"通道[{channel_tag}], "
            f"服务端最后已发送或已忽略的回报数据的回报编号[{rpt_msg_body.lastRptSeqNum}], "
            f"订阅的客户端环境号[{rpt_msg_body.subscribeEnvId}], "
            f"已订阅的回报消息种类[{rpt_msg_body.subscribeRptTypes}]")

        return 0

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
        channel_tag: str = channel.pChannelCfg.contents.channelTag.decode()

        print(
            f">>> 收到市场状态信息: "
            f"通道[{channel_tag}], "
            f"交易所代码[{rpt_msg_body.exchId}], "
            f"交易平台类型[{rpt_msg_body.platformId}], "
            f"市场类型[{rpt_msg_body.mktId}], "
            f"市场状态[{rpt_msg_body.mktState}]")

        return 0

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
        channel_tag: str = channel.pChannelCfg.contents.channelTag.decode()

        # OES通知消息 @see OesNotifyInfoReportT @note 若未依赖以下信息, 可不关注
        if rpt_msg_body.notifyType == eOesNotifyTypeT.OES_NOTIFY_TYPE_CRD_SECURITY_POSITION_UPDATE:
            # 融资融券证券头寸信息更新
            if rpt_msg_body.notifyScope == eOesNotifyScopeT.OES_NOTIFY_SCOPE_ALL:
                # 公共证券头寸信息已更新 @note 此处API端可主动查询 "指定的公共证券头寸" 来更新本地数据 @see OesApi_QueryCrdSecurityPosition
                print(
                    f">>> 公共证券头寸已更新! 通道[{channel_tag}], "
                    f"证券代码[{rpt_msg_body.securityId.decode()}], "
                    f"市场代码[{rpt_msg_body.mktId}]")
            else:
                # 专项证券头寸信息已更新 @note 此处API端可主动查询 "指定的专项证券头寸" 来更新本地数据 @see OesApi_QueryCrdSecurityPosition
                print(
                    f">>> 专项证券头寸已更新! 通道[{channel_tag}], "
                    f"证券代码[{rpt_msg_body.securityId.decode()}], "
                    f"市场代码[{rpt_msg_body.mktId}]")

        elif rpt_msg_body.notifyType == eOesNotifyTypeT.OES_NOTIFY_TYPE_CRD_CASH_POSITION_UPDATE:
            # 融资融券资金头寸信息更新 @note 暂未启用
            pass
        elif rpt_msg_body.notifyType == eOesNotifyTypeT.OES_NOTIFY_TYPE_CRD_COLLATERAL_INFO_UPDATE:
            # 融资融券担保品信息更新 @note 此处API端可主动查询 "指定的担保品信息" 来更新本地数据 @see OesApi_QueryStock
            pass
        elif rpt_msg_body.notifyType == eOesNotifyTypeT.OES_NOTIFY_TYPE_CRD_UNDERLYING_INFO_UPDATE:
            # 融资融券标的信息更新 @note 此处API端可主动查询 "指定的标的证券信息" 来更新本地数据 @see OesApi_QueryCrdUnderlyingInfo
            pass
        elif rpt_msg_body.notifyType == eOesNotifyTypeT.OES_NOTIFY_TYPE_CRD_MAINTENANCE_RATIO_UPDATE:
            # 融资融券维持担保比例更新 @note 此处API端可主动查询 "券商参数信息" 来更新本地数据 @see OesApi_QueryBrokerParamsInfo
            pass
        elif rpt_msg_body.notifyType == eOesNotifyTypeT.OES_NOTIFY_TYPE_CRD_LINE_OF_CERDIT_UPDATE:
            # 融资融券授信额度更新 @note 此处API端可主动查询 "信用资产信息" 来更新本地数据 @see OesApi_QueryCrdCreditAsset
            pass
        else:
            pass

        return 0

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
        print(">>> recv Test Request Rsp: "
                "msgId[{}], "
                "origSendTime[{}], "
                "respTime[{}], "
                "user_info[{}]".format(
            msg_head.msgId,
            msg_body.origSendTime.decode(),
            msg_body.respTime.decode(),
            user_info))

        return 0

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
        print(">>> recv Heart Beat: msgId[{}]".format(msg_head.msgId))

        return 0
    # -------------------------


    # ===================================================================
    # OES密码修改应答对应的回调函数
    # ===================================================================

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
        channel_tag: str = channel.pChannelCfg.contents.channelTag.decode()

        print(f">>> 收到修改密码的应答回报: "
            f"通道[{channel_tag}], "
            f"加密方法[{msg_body.encryptMethod}], "
            f"登录用户名[{msg_body.username}], "
            f"客户端编号[{msg_body.clientId}], "
            f"客户端环境号[{msg_body.clEnvId}], "
            f"发生日期[{msg_body.transDate}], "
            f"发生时间[{msg_body.transTime}], "
            f"拒绝原因[{msg_body.rejReason}]")
        return 0
    # -------------------------


    # ===================================================================
    # 期权结算单确认应答对应的回调函数
    # ===================================================================

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
        print(f">>> Recv option settlement confirm response message. "
            f"custId[{msg_body.optSettlementConfirmRsp.custId}], "
            f"rejReason[{msg_body.optSettlementConfirmRsp.rejReason}]")
        return 0
    # -------------------------


    # ===================================================================
    # OES查询接口对应的回调函数
    # ===================================================================

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
        print(f">>> 查询到委托信息: "
            f"index[{cursor.seqNo}], "
            f"isEnd[{'Y' if cursor.isEnd else 'N'}], "
            f"客户端环境号[{msg_body.clEnvId}], "
            f"客户委托流水号[{msg_body.clSeqNo}], "
            f"会员内部编号[{msg_body.clOrdId}], "
            f"证券账户[{msg_body.invAcctId.decode()}], "
            f"证券代码[{msg_body.securityId.decode()}], "
            f"市场代码[{msg_body.mktId}], "
            f"订单类型[{msg_body.ordType}], "
            f"买卖类型[{msg_body.bsType}], "
            f"委托状态[{msg_body.ordStatus}], "
            f"委托日期[{msg_body.ordDate}], "
            f"委托接收时间[{msg_body.ordTime}], "
            f"委托确认时间[{msg_body.ordCnfmTime}], "
            f"委托数量[{msg_body.ordQty}], "
            f"委托价格[{msg_body.ordPrice}], "
            f"撤单数量[{msg_body.canceledQty}], "
            f"累计成交份数[{msg_body.cumQty}], "
            f"累计成交金额[{msg_body.cumAmt}], "
            f"累计债券利息[{msg_body.cumInterest}], "
            f"累计交易佣金[{msg_body.cumFee}], "
            f"冻结交易金额[{msg_body.frzAmt}], "
            f"冻结债券利息[{msg_body.frzInterest}], "
            f"冻结交易佣金[{msg_body.frzFee}], "
            f"被撤内部委托编号[{msg_body.origClOrdId}], "
            f"拒绝原因[{msg_body.ordRejReason}], "
            f"交易所错误码[{msg_body.exchErrCode}]")

        return 0

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
        print(f">>> 查询到成交信息: "
            f"index[{cursor.seqNo}], "
            f"isEnd[{'Y' if cursor.isEnd else 'N'}], "
            f"成交编号[{msg_body.exchTrdNum}], "
            f"会员内部编号[{msg_body.clOrdId}], "
            f"委托客户端环境号[{msg_body.clEnvId}], "
            f"客户委托流水号[{msg_body.clSeqNo}], "
            f"证券账户[{msg_body.invAcctId.decode()}], "
            f"证券代码[{msg_body.securityId.decode()}], "
            f"市场代码[{msg_body.mktId}], "
            f"买卖方向[{msg_body.trdSide}], "
            f"委托买卖类型[{msg_body.ordBuySellType}], "
            f"成交日期[{msg_body.trdDate}], "
            f"成交时间[{msg_body.trdTime}], "
            f"成交数量[{msg_body.trdQty}], "
            f"成交价格[{msg_body.trdPrice}], "
            f"成交金额[{msg_body.trdAmt}], "
            f"累计成交数量[{msg_body.cumQty}], "
            f"累计成交金额[{msg_body.cumAmt}], "
            f"累计债券利息[{msg_body.cumInterest}], "
            f"累计交易费用[{msg_body.cumFee}], "
            f"PBU代码[{msg_body.pbuId}]")

        return 0

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
        print(f">>> 查询到资金信息: "
            f"index[{cursor.seqNo}], "
            f"isEnd[{'Y' if cursor.isEnd else 'N'}], "
            f"资金账户代码[{msg_body.cashAcctId.decode()}], "
            f"客户代码[{msg_body.custId.decode()}], "
            f"币种[{msg_body.currType}], "
            f"资金类型[{msg_body.cashType}], "
            f"期初余额[{msg_body.beginningBal}], "
            f"期初可用[{msg_body.beginningAvailableBal}], "
            f"期初可取[{msg_body.beginningDrawableBal}], "
            f"不可用[{msg_body.disableBal}], "
            f"累计存入[{msg_body.totalDepositAmt}], "
            f"累计提取[{msg_body.totalWithdrawAmt}], "
            f"当前提取冻结[{msg_body.withdrawFrzAmt}], "
            f"累计卖出[{msg_body.totalSellAmt}], "
            f"累计买入[{msg_body.totalBuyAmt}], "
            f"当前买冻结[{msg_body.buyFrzAmt}], "
            f"累计费用[{msg_body.totalFeeAmt}], "
            f"当前费用冻结[{msg_body.feeFrzAmt}], "
            f"当前维持保证金[{msg_body.marginAmt}], "
            f"当前保证金冻结[{msg_body.marginFrzAmt}], ",
            end="")

        if self.oes_api.get_business_type(channel) \
                == eOesBusinessTypeT.OES_BUSINESS_TYPE_OPTION:
            print(
                f"日初持仓保证金[{msg_body.optionExt.initialMargin}], "
                f"行权累计待交收冻结[{msg_body.optionExt.totalExerciseFrzAmt}], "
                f"未对冲实时价格保证金[{msg_body.optionExt.totalMarketMargin}], "
                f"已对冲实时价格保证金[{msg_body.optionExt.totalNetMargin}], "
                f"待追加保证金[{msg_body.optionExt.pendingSupplMargin}], ",
                end="")

        print(f"当前余额[{msg_body.currentTotalBal}], "
              f"当前可用[{msg_body.currentAvailableBal}], "
              f"当前可取[{msg_body.currentDrawableBal}]")

        return 0

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
        print(f">>> 查询到股票持仓信息: "
            f"index[{cursor.seqNo}], "
            f"isEnd[{'Y' if cursor.isEnd else 'N'}], "
            f"证券账户[{msg_body.invAcctId.decode()}], "
            f"市场代码[{msg_body.mktId}], "
            f"证券代码[{msg_body.securityId.decode()}], "
            f"日初持仓[{msg_body.originalHld}], "
            f"日初可用持仓[{msg_body.originalAvlHld}], "
            f"当日可减持额度[{msg_body.maxReduceQuota}], "
            f"日中累计买入[{msg_body.totalBuyHld}], "
            f"日中累计卖出[{msg_body.totalSellHld}], "
            f"当前卖出冻结[{msg_body.sellFrzHld}], "
            f"日中累计转换获得[{msg_body.totalTrsfInHld}], "
            f"日中累计转换付出[{msg_body.totalTrsfOutHld}], "
            f"当前转换付出冻结[{msg_body.trsfOutFrzHld}], "
            f"日初锁定[{msg_body.originalLockHld}], "
            f"累计锁定[{msg_body.totalLockHld}], "
            f"累计解锁[{msg_body.totalUnlockHld}], "
            f"当前总持仓[{msg_body.sumHld}], "
            f"当前可卖[{msg_body.sellAvlHld}], "
            f"当前可转换付出[{msg_body.trsfOutAvlHld}], "
            f"当前可锁定[{msg_body.lockAvlHld}]")

        return 0

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
        print(f">>> 查询到新股配号、中签信息: "
            f"index[{cursor.seqNo}], "
            f"isEnd[{'Y' if cursor.isEnd else 'N'}], "
            f"股东账户代码[{msg_body.invAcctId.decode()}], "
            f"证券代码[{msg_body.securityId.decode()}], "
            f"证券名称[{msg_body.securityName.decode()}], "
            f"市场代码[{msg_body.mktId}], "
            f"记录类型[{msg_body.lotType}], "
            f"失败原因[{msg_body.rejReason}], "
            f"配号、中签日期[{msg_body.lotDate}], "
            f"配号首个号码[{msg_body.assignNum}], "
            f"配号成功数量/中签股数[{msg_body.lotQty}], "
            f"最终发行价[{msg_body.lotPrice}], "
            f"中签金额[{msg_body.lotAmt}]")

        return 0

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
        print(f">>> 查询到客户信息: "
            f"index[{cursor.seqNo}], "
            f"isEnd[{'Y' if cursor.isEnd else 'N'}], "
            f"客户ID[{msg_body.custId.decode()}], "
            f"客户类型[{msg_body.custType}], "
            f"客户状态[{msg_body.status}], "
            f"风险评级[{msg_body.riskLevel}], "
            f"机构标志[{msg_body.institutionFlag}], "
            f"投资者分类[{msg_body.investorClass}]")

        return 0

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
        print(f">>> 查询到证券账户信息: "
            f"index[{cursor.seqNo}], "
            f"isEnd[{'Y' if cursor.isEnd else 'N'}], "
            f"证券账户[{msg_body.invAcctId.decode()}], "
            f"市场代码[{msg_body.mktId}], "
            f"客户代码[{msg_body.custId.decode()}], "
            f"账户状态[{msg_body.status}], "
            f"主板权益[{msg_body.subscriptionQuota}], "
            f"科创板权益[{msg_body.kcSubscriptionQuota}]")

        return 0

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

        print(f">>> 查询到佣金信息: "
            f"index[{cursor.seqNo}], "
            f"isEnd[{'Y' if cursor.isEnd else 'N'}], "
            f"客户代码[{msg_body.custId.decode()}], "
            f"证券代码[{msg_body.securityId.decode()}], "
            f"市场代码[{msg_body.mktId}], "
            f"证券类型[{msg_body.securityType}], "
            f"证券子类型[{msg_body.subSecurityType}], "
            f"买卖类型[{msg_body.bsType}], "
            f"币种[{msg_body.currType}], "
            f"费用标识[{msg_body.feeType}], "
            f"计算模式 [{msg_body.calcFeeMode}], "
            f"费率[{msg_body.feeRate}], "
            f"最低费用[{msg_body.minFee}], "
            f"最高费用[{msg_body.maxFee}]")

        return 0

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
        if msg_body.direct == eOesFundTrsfDirectT.OES_FUND_TRSF_DIRECT_IN:
            direction = "入金"
        else:
            direction = "出金"

        print(f">>> 查询到出入金流水: "
            f"index[{cursor.seqNo}], "
            f"isEnd[{'Y' if cursor.isEnd else 'N'}], "
            f"客户端环境号[{msg_body.clEnvId}], "
            f"客户委托流水号[{msg_body.clSeqNo}], "
            f"资金账户[{msg_body.cashAcctId.decode()}], "
            f"方向[{direction}], "
            f"金额[{msg_body.occurAmt}], "
            f"出入金状态[{msg_body.trsfStatus}], "
            f"错误原因[{msg_body.rejReason}], "
            f"主柜错误码[{msg_body.counterErrCode}], "
            f"错误信息[{msg_body.errorInfo.decode()}], "
            f"柜台委托编码[{msg_body.counterEntrustNo}], "
            f"接收日期[{msg_body.operDate}], "
            f"接收时间[{msg_body.operTime}], "
            f"上报时间[{msg_body.dclrTime}], "
            f"完成时间[{msg_body.doneTime}]")

        return 0

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
        print(f">>> 查询到证券发行产品信息: "
            f"index[{cursor.seqNo}], "
            f"isEnd[{'Y' if cursor.isEnd else 'N'}], "
            f"证券代码[{msg_body.securityId.decode()}], "
            f"证券名称[{msg_body.securityName.decode()}], "
            f"正股代码[{msg_body.underlyingSecurityId.decode()}], "
            f"市场代码[{msg_body.mktId}], "
            f"证券类型[{msg_body.securityType}], "
            f"证券子类型[{msg_body.subSecurityType}], "
            f"是否允许撤单[{msg_body.isCancelAble}], "
            f"是否允许重复认购[{msg_body.isReApplyAble}], "
            f"发行起始时间[{msg_body.startDate}], "
            f"发行结束时间[{msg_body.endDate}], "
            f"发行总量[{msg_body.issueQty}], "
            f"份数单位[{msg_body.qtyUnit}], "
            f"最大份数[{msg_body.ordMaxQty}], "
            f"最小份数[{msg_body.ordMinQty}], "
            f"发行价格[{msg_body.issuePrice}], "
            f"价格上限[{msg_body.upperLimitPrice}], "
            f"价格下限[{msg_body.lowerLimitPrice}]")

        return 0

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
        print(f">>> 查询到现货产品信息: "
            f"index[{cursor.seqNo}], "
            f"isEnd[{'Y' if cursor.isEnd else 'N'}], "
            f"证券代码[{msg_body.securityId.decode()}], "
            f"证券名称[{msg_body.securityName.decode()}], "
            f"基金代码[{msg_body.fundId.decode()}], "
            f"市场代码[{msg_body.mktId}], "
            f"证券类型[{msg_body.securityType}], "
            f"证券子类型[{msg_body.subSecurityType}], "
            f"证券级别[{msg_body.securityLevel}], "
            f"风险等级[{msg_body.securityRiskLevel}], "
            f"停牌标志[{msg_body.suspFlag}], "
            f"适当性管理[{msg_body.qualificationClass}], "
            f"当日回转[{msg_body.isDayTrading}], "
            f"是否注册制[{msg_body.isRegistration}], "
            f"价格单位[{msg_body.priceTick}], "
            f"买份数单位[{msg_body.lmtBuyQtyUnit}], "
            f"卖份数单位[{msg_body.lmtSellQtyUnit}], "
            f"昨日收盘价[{msg_body.prevClose}], "
            f"债券利息[{msg_body.bondInterest}], "
            f"涨停价[{msg_body.priceLimit[eOesTrdSessTypeT.OES_TRD_SESS_TYPE_T].upperLimitPrice}], "
            f"跌停价[{msg_body.priceLimit[eOesTrdSessTypeT.OES_TRD_SESS_TYPE_T].lowerLimitPrice}]")

        return 0

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
        print(f">>> 查询到ETF申赎产品信息: "
            f"index[{cursor.seqNo}], "
            f"isEnd[{'Y' if cursor.isEnd else 'N'}], "
            f"基金代码[{msg_body.fundId.decode()}], "
            f"证券代码[{msg_body.securityId.decode()}], "
            f"市场代码[{msg_body.mktId}], "
            f"申购赎回单位[{msg_body.creRdmUnit}], "
            f"最大现金替代比例[{msg_body.maxCashRatio}], "
            f"前一日最小申赎单位净值[{msg_body.navPerCU}], "
            f"前一日现金差额[{msg_body.cashCmpoent}], "
            f"成份证券数目[{msg_body.componentCnt}]")

        return 0

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
        print(f">>> 查询到ETF成份证券信息: "
            f"index[{cursor.seqNo}], "
            f"isEnd[{'Y' if cursor.isEnd else 'N'}], "
            f"ETF基金申赎代码[{msg_body.fundId.decode()}], "
            f"成份证券代码[{msg_body.securityId.decode()}], "
            f"成份证券名称[{msg_body.securityName.decode()}], "
            f"成份证券市场代码[{msg_body.mktId}], "
            f"ETF基金市场代码[{msg_body.fundMktId}], "
            f"现金替代标识[{msg_body.subFlag}], "
            f"是否申赎对价[{msg_body.isTrdComponent}], "
            f"前收盘价[{msg_body.prevClose}], "
            f"成份证券数量[{msg_body.qty}], "
            f"申购溢价比例[{msg_body.premiumRatio}], "
            f"赎回折价比例[{msg_body.discountRatio}], "
            f"申购替代金额[{msg_body.creationSubCash}], "
            f"赎回替代金额[{msg_body.redemptionSubCash}]")

        return 0

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
        print(f">>> 查询到市场状态信息: "
            f"index[{cursor.seqNo}], "
            f"isEnd[{'Y' if cursor.isEnd else 'N'}], "
            f"交易所代码[{msg_body.exchId}], "
            f"交易平台类型[{msg_body.platformId}], "
            f"市场类型[{msg_body.mktId}], "
            f"市场状态[{msg_body.mktState}]")

        return 0

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
        print(f">>> 查询到通知消息: "
            f"index[{cursor.seqNo}], "
            f"isEnd[{'Y' if cursor.isEnd else 'N'}], "
            f"通知消息序号[{msg_body.notifySeqNo}], "
            f"通知消息等级[{msg_body.notifyLevel}], "
            f"通知消息范围[{msg_body.notifyScope}], "
            f"通知来源分类[{msg_body.notifySource}], "
            f"通知消息类型[{msg_body.notifyType}], "
            f"通知发出时间[{msg_body.tranTime}], "
            f"客户代码[{msg_body.custId.decode()}], "
            f"通知内容[{msg_body.content}]")

        return 0

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
        print(f">>> 查询到期权产品信息: "
            f"index[{cursor.seqNo}], "
            f"isEnd[{'Y' if cursor.isEnd else 'N'}], "
            f"证券代码[{msg_body.securityId.decode()}], "
            f"合约交易代码[{msg_body.contractId.decode()}], "
            f"合约名称[{msg_body.securityName.decode()}], "
            f"标的证券[{msg_body.underlyingSecurityId.decode()}], "
            f"市场代码[{msg_body.mktId}], "
            f"产品类型[{msg_body.productType}], "
            f"证券类型[{msg_body.securityType}], "
            f"证券子类型[{msg_body.subSecurityType}], "
            f"合约类型[{msg_body.contractType}], "
            f"行权方式[{msg_body.exerciseType}], "
            f"交割方式[{msg_body.deliveryType}], "
            f"当日回转[{msg_body.isDayTrading}], "
            f"限制开仓[{msg_body.limitOpenFlag}], "
            f"连续停牌[{msg_body.suspFlag}], "
            f"临时停牌[{msg_body.temporarySuspFlag}], "
            f"合约单位[{msg_body.contractUnit}], "
            f"期权行权价[{msg_body.exercisePrice}], "
            f"交割日期[{msg_body.deliveryDate}], "
            f"交割月份[{msg_body.deliveryMonth}], "
            f"上市日期[{msg_body.listDate}], "
            f"最后交易日[{msg_body.lastTradeDay}], "
            f"行权起始日[{msg_body.exerciseBeginDate}], "
            f"行权结束日[{msg_body.exerciseEndDate}], "
            f"持仓量[{msg_body.contractPosition}], "
            f"前收盘价[{msg_body.prevClosePrice}], "
            f"前结算价[{msg_body.prevSettlPrice}], "
            f"标的前收[{msg_body.underlyingClosePrice}], "
            f"报价单位[{msg_body.priceTick}], "
            f"涨停价[{msg_body.upperLimitPrice}], "
            f"跌停价[{msg_body.lowerLimitPrice}], "
            f"买单位[{msg_body.buyQtyUnit}], "
            f"限价买上限[{msg_body.lmtBuyMaxQty}], "
            f"限价买下限[{msg_body.lmtBuyMinQty}], "
            f"市价买上限[{msg_body.mktBuyMaxQty}], "
            f"市价买下限[{msg_body.mktBuyMinQty}], "
            f"卖单位[{msg_body.sellQtyUnit}], "
            f"限价卖上限[{msg_body.lmtSellMaxQty}], "
            f"限价卖下限[{msg_body.lmtSellMinQty}], "
            f"市价卖上限[{msg_body.mktSellMaxQty}], "
            f"市价卖下限[{msg_body.mktSellMinQty}], "
            f"卖开保证金[{msg_body.sellMargin}], "
            f"保证金参数一[{msg_body.marginRatioParam1}](万分比), "
            f"保证金参数二[{msg_body.marginRatioParam2}](万分比), "
            f"保证金上浮比例[{msg_body.increasedMarginRatio}](万分比), "
            f"合约状态[{chr(msg_body.securityStatusFlag[0])}{chr(msg_body.securityStatusFlag[1])}"
            f"{chr(msg_body.securityStatusFlag[2])}{chr(msg_body.securityStatusFlag[3])}"
            f"{chr(msg_body.securityStatusFlag[4])}{chr(msg_body.securityStatusFlag[5])}"
            f"{chr(msg_body.securityStatusFlag[6])}{chr(msg_body.securityStatusFlag[7])}]")

        return 0

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
        print(f">>> 查询到期权持仓信息: "
            f"index[{cursor.seqNo}], "
            f"isEnd[{'Y' if cursor.isEnd else 'N'}], "
            f"证券账户[{msg_body.invAcctId.decode()}], "
            f"合约代码[{msg_body.securityId.decode()}], "
            f"市场代码[{msg_body.mktId}], "
            f"持仓类型[{msg_body.positionType}], "
            f"产品类型[{msg_body.productType}], "
            f"证券类型[{msg_body.securityType}], "
            f"证券子类型[{msg_body.subSecurityType}], "
            f"合约类型[{msg_body.contractType}], "
            f"日初持仓张数[{msg_body.originalQty}], "
            f"日初可用持仓张数[{msg_body.originalAvlQty}], "
            f"日初总持仓成本[{msg_body.originalCostAmt}], "
            f"日中累计开仓张数[{msg_body.totalOpenQty}], "
            f"开仓未成交张数[{msg_body.uncomeQty}], "
            f"日中累计平仓张数[{msg_body.totalCloseQty}], "
            f"平仓在途冻结张数[{msg_body.closeFrzQty}], "
            f"手动冻结张数[{msg_body.manualFrzQty}], "
            f"日中累计获得权利金[{msg_body.totalInPremium}], "
            f"日中累计支出权利金[{msg_body.totalOutPremium}], "
            f"日中累计开仓费用[{msg_body.totalOpenFee}], "
            f"日中累计平仓费用[{msg_body.totalCloseFee}], "
            f"权利仓行权冻结张数[{msg_body.exerciseFrzQty}], "
            f"义务仓持仓保证金[{msg_body.positionMargin}], "
            f"可平仓张数[{msg_body.closeAvlQty}], "
            f"可行权张数[{msg_body.exerciseAvlQty}], "
            f"总持仓张数[{msg_body.sumQty}], "
            f"持仓成本价[{msg_body.costPrice}], "
            f"可备兑标的券数量[{msg_body.coveredAvlUnderlyingQty}]")

        return 0

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
        """
        print(f">>> 期权标的持仓信息: "
            f"index[{cursor.seqNo}], "
            f"isEnd[{'Y' if cursor.isEnd else 'N'}], "
            f"证券账户[{msg_body.invAcctId.decode()}], "
            f"标的证券代码[{msg_body.underlyingSecurityId.decode()}], "
            f"市场代码[{msg_body.mktId}], "
            f"标的市场代码[{msg_body.underlyingMktId}], "
            f"标的证券类型[{msg_body.underlyingSecurityType}], "
            f"标的证券子类型[{msg_body.underlyingSubSecurityType}], "
            f"日初标的证券的总持仓数量[{msg_body.originalHld}], "
            f"日初标的证券的可用持仓数量[{msg_body.originalAvlHld}], "
            f"日初备兑仓实际占用的标的证券数量[{msg_body.originalCoveredQty}], "
            f"日初备兑仓应占用的标的证券数量[{msg_body.initialCoveredQty}], "
            f"当前备兑仓实际占用的标的证券数量[{msg_body.coveredQty}], "
            f"当前备兑仓占用标的证券的缺口数量[{msg_body.coveredGapQty}], "
            f"当前可用于备兑开仓的标的持仓数量[{msg_body.coveredAvlQty}], "
            f"当前可锁定的标的持仓数量[{msg_body.lockAvlQty}], "
            f"标的证券总持仓数量[{msg_body.sumHld}], "
            f"标的证券当日最大可减持额度[{msg_body.maxReduceQuota}]")

        return 0

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
        print(f">>> 期权限仓额度信息: "
            f"index[{cursor.seqNo}], "
            f"isEnd[{'Y' if cursor.isEnd else 'N'}], "
            f"证券账户[{msg_body.invAcctId.decode()}], "
            f"标的证券代码[{msg_body.underlyingSecurityId.decode()}], "
            f"市场代码[{msg_body.mktId}], "
            f"标的市场代码[{msg_body.underlyingMktId}], "
            f"标的证券类型[{msg_body.underlyingSecurityType}], "
            f"标的证券子类型[{msg_body.underlyingSubSecurityType}], "
            f"总持仓限额[{msg_body.totalPositionLimit}], "
            f"权利仓限额[{msg_body.longPositionLimit}], "
            f"单日买入开仓限额[{msg_body.dailyBuyOpenLimit}], "
            f"日初权利仓持仓数量[{msg_body.originalLongQty}], "
            f"日初义务仓持仓数量[{msg_body.originalShortQty}], "
            f"日初备兑义务仓持仓数量[{msg_body.originalCoveredQty}], "
            f"未占用的总持仓限额[{msg_body.availableTotalPositionLimit}], "
            f"未占用的权利仓限额[{msg_body.availableLongPositionLimit}], "
            f"未占用的单日买入开仓限额[{msg_body.availableDailyBuyOpenLimit}]")

        return 0

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
        print(f">>> 期权限购额度信息: index[{cursor.seqNo}], "
            f"isEnd[{'Y' if cursor.isEnd else 'N'}], "
            f"客户代码[{msg_body.custId.decode()}], "
            f"资金账号[{msg_body.cashAcctId.decode()}], "
            f"股东账号[{msg_body.invAcctId.decode()}], "
            f"市场代码[{msg_body.mktId}], "
            f"客户类别[{msg_body.custType}], "
            f"限购额度[{msg_body.purchaseLimit}], "
            f"日初占用限购额度[{msg_body.originalUsedPurchaseAmt}], "
            f"日中累计开仓额度[{msg_body.totalOpenPurchaseAmt}], "
            f"当前挂单冻结额度[{msg_body.frzPurchaseAmt}], "
            f"日中累计平仓额度[{msg_body.totalClosePurchaseAmt}], "
            f"当前可用限购额度[{msg_body.availablePurchaseLimit}]")

        return 0

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
        print(f">>> 查询到行权指派消息: "
            f"index[{cursor.seqNo}], "
            f"isEnd[{'Y' if cursor.isEnd else 'N'}],"
            f"证券账户[{msg_body.invAcctId.decode()}], "
            f"期权合约代码[{msg_body.securityId.decode()}], "
            f"期权合约名称[{msg_body.securityName.decode()}], "
            f"市场代码[{msg_body.mktId}], "
            f"持仓方向[{msg_body.positionType}], "
            f"产品类型[{msg_body.productType}], "
            f"证券类型[{msg_body.securityType}], "
            f"证券子类型[{msg_body.subSecurityType}], "
            f"合约类型[{msg_body.contractType}], "
            f"交割方式[{msg_body.deliveryType}], "
            f"行权价格[{msg_body.exercisePrice}], "
            f"行权张数[{msg_body.exerciseQty}], "
            f"标的证券收付数量[{msg_body.deliveryQty}], "
            f"行权开始日期[{msg_body.exerciseBeginDate}], "
            f"行权结束日期[{msg_body.exerciseEndDate}], "
            f"清算日期[{msg_body.clearingDate}], "
            f"交收日期[{msg_body.deliveryDate}], "
            f"清算金额[{msg_body.clearingAmt}], "
            f"清算费用[{msg_body.clearingFee}], "
            f"收付金额[{msg_body.settlementAmt}], "
            f"标的证券代码[{msg_body.underlyingSecurityId.decode()}], "
            f"标的市场代码[{msg_body.underlyingMktId}], "
            f"标的证券类型[{msg_body.underlyingSecurityType}]")

        return 0

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
        print(f">>> 查询到融资融券合约消息: "
            f"index[{cursor.seqNo}], "
            f"isEnd[{'Y' if cursor.isEnd else 'N'}], "
            f"合约编号[{msg_body.debtId}], "
            f"资金账户代码[{msg_body.cashAcctId.decode()}], "
            f"股东账户代码[{msg_body.invAcctId.decode()}], "
            f"证券代码[{msg_body.securityId.decode()}], "
            f"市场代码[{msg_body.mktId}], "
            f"证券类型[{msg_body.securityType}], "
            f"证券子类型[{msg_body.subSecurityType}], "
            f"证券的产品类型[{msg_body.securityProductType}], "
            f"负债类型[{msg_body.debtType}], "
            f"负债状态[{msg_body.debtStatus}], "
            f"期初负债状态[{msg_body.originalDebtStatus}], "
            f"负债归还模式[{msg_body.debtRepayMode}], "
            f"委托日期[{msg_body.ordDate}], "
            f"委托价格[{msg_body.ordPrice}], "
            f"委托数量[{msg_body.ordQty}], "
            f"成交数量[{msg_body.trdQty}], "
            f"委托金额[{msg_body.ordAmt}], "
            f"成交金额[{msg_body.trdAmt}], "
            f"成交费用[{msg_body.trdFee}], "
            f"实时合约金额[{msg_body.currentDebtAmt}], "
            f"实时合约手续费[{msg_body.currentDebtFee}], "
            f"实时合约利息[{msg_body.currentDebtInterest}], "
            f"实时合约数量[{msg_body.currentDebtQty}], "
            f"在途冻结数量[{msg_body.uncomeDebtQty}], "
            f"在途冻结金额[{msg_body.uncomeDebtAmt}], "
            f"在途冻结手续费[{msg_body.uncomeDebtFee}], "
            f"在途冻结利息[{msg_body.uncomeDebtInterest}], "
            f"累计已归还金额[{msg_body.totalRepaidAmt}], "
            f"累计已归还手续费[{msg_body.totalRepaidFee}], "
            f"累计已归还利息[{msg_body.totalRepaidInterest}], "
            f"累计已归还数量[{msg_body.totalRepaidQty}], "
            f"期初待归还金额[{msg_body.originalDebtAmt}], "
            f"期初待归还手续费[{msg_body.originalDebtFee}], "
            f"期初待归还利息[{msg_body.originalDebtInterest}], "
            f"期初待归还数量[{msg_body.originalDebtQty}], "
            f"期初已归还数量[{msg_body.originalRepaidQty}], "
            f"期初已归还金额[{msg_body.originalRepaidAmt}], "
            f"期初已归还利息[{msg_body.originalRepaidInterest}], "
            f"罚息[{msg_body.punishInterest}], "
            f"保证金比例[{msg_body.marginRatio}], "
            f"融资利率/融券费率[{msg_body.interestRate}], "
            f"负债截止日期[{msg_body.repayEndDate}], "
            f"头寸编号[{msg_body.cashGroupNo}], "
            f"展期次数[{msg_body.postponeTimes}], "
            f"展期状态[{msg_body.postponeStatus}], "
            f"同一证券所有融券合约的合计待归还负债数量[{msg_body.securityRepayableDebtQty}], "
            f"该融券合约的当前待归还负债数量[{msg_body.contractRepayableDebtQty}]")

        return 0

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
        print(f">>> 查询到融资融券客户单证券负债统计信息: "
            f"index[{cursor.seqNo}], "
            f"isEnd[{'Y' if cursor.isEnd else 'N'}], "
            f"股东账户代码[{msg_body.invAcctId.decode()}], "
            f"证券代码[{msg_body.securityId.decode()}], "
            f"市场代码[{msg_body.mktId}], "
            f"产品类型[{msg_body.productType}], "
            f"证券类型[{msg_body.securityType}], "
            f"证券子类型[{msg_body.subSecurityType}], "
            f"是否为融资融券可充抵保证金证券[{msg_body.isCrdCollateral}], "
            f"是否为融资标的[{msg_body.isCrdMarginTradeUnderlying}], "
            f"是否为融券标的[{msg_body.isCrdShortSellUnderlying}], "
            f"融资融券可充抵保证金证券的交易状态[{msg_body.isCrdCollateralTradable}], "
            f"可充抵保证金折算率[{msg_body.collateralRatio}], "
            f"融资买入保证金比例[{msg_body.marginBuyRatio}], "
            f"融券卖出保证金比例[{msg_body.shortSellRatio}], "
            f"市值计算使用的证券价格[{msg_body.marketCapPrice}], "
            f"可卖持仓数量[{msg_body.sellAvlHld}], "
            f"可划出持仓数量[{msg_body.trsfOutAvlHld}], "
            f"直接还券可用持仓数量[{msg_body.repayStockDirectAvlHld}], "
            f"同一证券所有融券合约的合计待归还负债数量[{msg_body.shortSellRepayableDebtQty}], "
            f"专项证券头寸数量 (含已用)[{msg_body.specialSecurityPositionQty}], "
            f"专项证券头寸已用数量 (含尚未成交的在途冻结数量)"
            f"[{msg_body.specialSecurityPositionUsedQty}], "
            f"专项证券头寸可用数量[{msg_body.specialSecurityPositionAvailableQty}], "
            f"公共证券头寸数量 (含已用)[{msg_body.publicSecurityPositionQty}], "
            f"公共证券头寸可用数量[{msg_body.publicSecurityPositionAvailableQty}], "
            f"总持仓数量[{msg_body.collateralHoldingQty}], "
            f"在途买入数量[{msg_body.collateralUncomeBuyQty}], "
            f"在途转入持仓数量[{msg_body.collateralUncomeTrsfInQty}], "
            f"在途卖出冻结的持仓数量[{msg_body.collateralUncomeSellQty}], "
            f"转出冻结的持仓数量[{msg_body.collateralTrsfOutQty}], "
            f"直接还券冻结的持仓数量[{msg_body.collateralRepayDirectQty}], "
            f"融资负债金额[{msg_body.marginBuyDebtAmt}], "
            f"融资交易费用[{msg_body.marginBuyDebtFee}], "
            f"融资负债利息[{msg_body.marginBuyDebtInterest}], "
            f"融资负债数量[{msg_body.marginBuyDebtQty}], "
            f"在途融资买入金额[{msg_body.marginBuyUncomeAmt}], "
            f"在途融资交易费用[{msg_body.marginBuyUncomeFee}], "
            f"在途融资利息[{msg_body.marginBuyUncomeInterest}], "
            f"在途融资数量[{msg_body.marginBuyUncomeQty}], "
            f"日初融资负债金额[{msg_body.marginBuyOriginDebtAmt}], "
            f"日初融资负债数量[{msg_body.marginBuyOriginDebtQty}], "
            f"当日已归还融资金额[{msg_body.marginBuyRepaidAmt}], "
            f"当日已归还融资数量[{msg_body.marginBuyRepaidQty}], "
            f"融券负债金额[{msg_body.shortSellDebtAmt}], "
            f"融券交易费用[{msg_body.shortSellDebtFee}], "
            f"融券负债利息[{msg_body.shortSellDebtInterest}], "
            f"融券负债数量[{msg_body.shortSellDebtQty}], "
            f"在途融券卖出金额[{msg_body.shortSellUncomeAmt}], "
            f"在途融券交易费用[{msg_body.shortSellUncomeFee}], "
            f"在途融券利息[{msg_body.shortSellUncomeInterest}], "
            f"在途融券数量[{msg_body.shortSellUncomeQty}], "
            f"日初融券负债数量[{msg_body.shortSellOriginDebtQty}], "
            f"当日已归还融券数量[{msg_body.shortSellRepaidQty}], "
            f"在途归还融券数量[{msg_body.shortSellUncomeRepaidQty}], "
            f"当日已归还融券金额[{msg_body.shortSellRepaidAmt}], "
            f"当日实际归还融券金额[{msg_body.shortSellRealRepaidAmt}], "
            f"其它负债的负债金额[{msg_body.otherDebtAmt}], "
            f"其它负债利息[{msg_body.otherDebtInterest}]")

        return 0

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
        print(f">>> 查询到信用资产信息: index[{cursor.seqNo}], "
            f"isEnd[{'Y' if cursor.isEnd else 'N'}], "
            f"资金账户代码[{msg_body.cashAcctId.decode()}], "
            f"客户代码[{msg_body.custId.decode()}], "
            f"币种[{msg_body.currType}], "
            f"资金帐户类别[{msg_body.cashType}], "
            f"资金帐户状态[{msg_body.cashAcctStatus}], "
            f"总资产[{msg_body.totalAssetValue}], "
            f"总负债[{msg_body.totalDebtValue}], "
            f"维持担保比例[{msg_body.maintenaceRatio}], "
            f"保证金可用余额[{msg_body.marginAvailableBal}], "
            f"现金余额[{msg_body.cashBalance}], "
            f"可用余额[{msg_body.availableBal}], "
            f"可取余额[{msg_body.drawableBal}], "
            f"买担保品可用余额[{msg_body.buyCollateralAvailableBal}], "
            f"买券还券可用余额[{msg_body.repayStockAvailableBal}], "
            f"融券卖出所得总额[{msg_body.shortSellGainedAmt}], "
            f"融券卖出所得可用金额[{msg_body.shortSellGainedAvailableAmt}], "
            f"日中累计已用于归还负债的资金总额[{msg_body.totalRepaidAmt}], "
            f"日中为归还负债而在途冻结的资金总额[{msg_body.repayFrzAmt}], "
            f"融资买入授信额度[{msg_body.marginBuyMaxQuota}], "
            f"融券卖出授信额度[{msg_body.shortSellMaxQuota}], "
            f"融资融券总授信额度[{msg_body.creditTotalMaxQuota}], "
            f"融资买入已用授信额度[{msg_body.marginBuyUsedQuota}], "
            f"融资买入可用授信额度[{msg_body.marginBuyAvailableQuota}], "
            f"融券卖出已用授信额度[{msg_body.shortSellUsedQuota}], "
            f"融券卖出可用授信额度[{msg_body.shortSellAvailableQuota}], "
            f"专项资金头寸金额[{msg_body.specialCashPositionAmt}], "
            f"专项资金头寸可用余额[{msg_body.specialCashPositionAvailableBal}], "
            f"公共资金头寸金额[{msg_body.publicCashPositionAmt}], "
            f"公共资金头寸可用余额[{msg_body.publicCashPositionAvailableBal}], "
            f"证券持仓总市值[{msg_body.collateralHoldingMarketCap}], "
            f"在途卖出证券持仓市值[{msg_body.collateralUncomeSellMarketCap}], "
            f"转出冻结的证券持仓市值[{msg_body.collateralTrsfOutMarketCap}], "
            f"直接还券冻结的证券持仓市值[{msg_body.collateralRepayDirectMarketCap}], "
            f"融资负债金额[{msg_body.marginBuyDebtAmt}], "
            f"融资负债交易费用[{msg_body.marginBuyDebtFee}], "
            f"融资负债利息[{msg_body.marginBuyDebtInterest}], "
            f"在途融资金额[{msg_body.marginBuyUncomeAmt}], "
            f"在途融资交易费用[{msg_body.marginBuyUncomeFee}], "
            f"在途融资利息[{msg_body.marginBuyUncomeInterest}], "
            f"融资买入证券市值[{msg_body.marginBuyDebtMarketCap}], "
            f"融资买入负债占用的保证金金额[{msg_body.marginBuyDebtUsedMargin}], "
            f"融券卖出金额[{msg_body.shortSellDebtAmt}], "
            f"融券负债交易费用[{msg_body.shortSellDebtFee}], "
            f"融券负债利息[{msg_body.shortSellDebtInterest}], "
            f"在途融券卖出金额[{msg_body.shortSellUncomeAmt}], "
            f"在途融券交易费用[{msg_body.shortSellUncomeFee}], "
            f"在途融券利息[{msg_body.shortSellUncomeInterest}], "
            f"融券卖出证券市值[{msg_body.shortSellDebtMarketCap}], "
            f"融券卖出负债占用的保证金金额[{msg_body.shortSellDebtUsedMargin}], "
            f"其他负债金额[{msg_body.otherDebtAmt}], "
            f"其他负债利息[{msg_body.otherDebtInterest}], "
            f"融资融券其他费用[{msg_body.otherCreditFee}], "
            f"融资融券专项头寸总费用[{msg_body.creditTotalSpecialFee}], "
            f"融资专项头寸成本费[{msg_body.marginBuySpecialFee}], "
            f"融券专项头寸成本费[{msg_body.shortSellSpecialFee}], "
            f"其它担保资产价值[{msg_body.otherBackedAssetValue}], "
            f"修正资产金额[{msg_body.correctAssetValue}], "
            f"可转出资产价值[{msg_body.trsfOutAbleAssetValue}], "
            f"标的证券市值[{msg_body.underlyingMarketCap}]")

        return 0

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
        print(f">>> 查询到融资融券直接还款委托信息: "
            f"index[{cursor.seqNo}], "
            f"isEnd[{'Y' if cursor.isEnd else 'N'}], "
            f"资金账户代码[{msg_body.cashAcctId.decode()}], "
            f"指定归还的合约编号[{msg_body.debtId}], "
            f"证券账户[{msg_body.invAcctId.decode()}], "
            f"证券代码[{msg_body.securityId.decode()}], "
            f"客户委托流水号[{msg_body.clSeqNo}], "
            f"市场代码[{msg_body.mktId}], "
            f"归还模式[{msg_body.repayMode}], "
            f"归还指令类型[{msg_body.repayJournalType}], "
            f"归还金额[{msg_body.repayAmt}], "
            f"委托日期[{msg_body.ordDate}], "
            f"委托时间[{msg_body.ordTime}], "
            f"客户订单编号[{msg_body.clOrdId}], "
            f"客户端编号[{msg_body.clientId}], "
            f"客户端环境号[{msg_body.clEnvId}], "
            f"委托强制标志[{msg_body.mandatoryFlag}], "
            f"订单当前状态[{msg_body.ordStatus}], "
            f"所有者类型[{msg_body.ownerType}], "
            f"订单拒绝原因[{msg_body.ordRejReason}], "
            f"实际归还数量[{msg_body.repaidQty}], "
            f"实际归还金额[{msg_body.repaidAmt}], "
            f"实际归还费用[{msg_body.repaidFee}], "
            f"实际归还利息[{msg_body.repaidInterest}], "
            f"营业部编号[{msg_body.branchId}]")

        return 0

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
        print(f">>> 查询到融资融券资金头寸信息: "
            f"index[{cursor.seqNo}], "
            f"isEnd[{'Y' if cursor.isEnd else 'N'}], "
            f"客户代码[{msg_body.custId.decode()}], "
            f"资金账户代码[{msg_body.cashAcctId.decode()}], "
            f"头寸编号[{msg_body.cashGroupNo}], "
            f"头寸性质[{msg_body.cashGroupProperty}], "
            f"币种[{msg_body.currType}], "
            f"资金头寸金额[{msg_body.positionAmt}], "
            f"日间已归还金额[{msg_body.repaidPositionAmt}], "
            f"累计已用金额[{msg_body.usedPositionAmt}], "
            f"当前尚未成交的在途冻结金额[{msg_body.frzPositionAmt}], "
            f"期初余额[{msg_body.originalBalance}], "
            f"期初可用余额[{msg_body.originalAvailable}], "
            f"期初已用金额[{msg_body.originalUsed}], "
            f"总计调整金额[{msg_body.totalAdjustAmt}], "
            f"资金头寸剩余可融资金额[{msg_body.availableBalance}]")

        return 0

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
        print(f">>> 查询到融资融券证券头寸信息: "
            f"index[{cursor.seqNo}], "
            f"isEnd[{'Y' if cursor.isEnd else 'N'}], "
            f"客户代码[{msg_body.custId.decode()}], "
            f"证券账户[{msg_body.invAcctId.decode()}], "
            f"证券代码[{msg_body.securityId.decode()}], "
            f"市场代码[{msg_body.mktId}], "
            f"头寸性质[{msg_body.cashGroupProperty}], "
            f"头寸编号[{msg_body.cashGroupNo}], "
            f"证券头寸数量[{msg_body.positionQty}], "
            f"日间已归还数量[{msg_body.repaidPositionQty}], "
            f"累计已用数量[{msg_body.usedPositionQty}], "
            f"当前尚未成交的在途冻结数量[{msg_body.frzPositionQty}], "
            f"期初数量[{msg_body.originalBalanceQty}], "
            f"期初可用数量[{msg_body.originalAvailableQty}], "
            f"期初已用数量[{msg_body.originalUsedQty}], "
            f"当前可用头寸数量[{msg_body.availablePositionQty}]")

        return 0

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
        print(f">>> 查询到信用持仓信息: "
            f"index[{cursor.seqNo}], "
            f"isEnd[{'Y' if cursor.isEnd else 'N'}], "
            f"证券账户[{msg_body.invAcctId.decode()}], "
            f"市场代码[{msg_body.mktId}], "
            f"证券代码[{msg_body.securityId.decode()}], "
            f"日初持仓[{msg_body.originalHld}], "
            f"日初可用持仓[{msg_body.originalAvlHld}], "
            f"当日可减持额度[{msg_body.maxReduceQuota}], "
            f"日中累计买入[{msg_body.totalBuyHld}], "
            f"日中累计卖出[{msg_body.totalSellHld}], "
            f"当前卖出冻结[{msg_body.sellFrzHld}], "
            f"日中累计转换获得[{msg_body.totalTrsfInHld}], "
            f"日中累计转换付出[{msg_body.totalTrsfOutHld}], "
            f"当前转换付出冻结[{msg_body.trsfOutFrzHld}], "
            f"日初锁定[{msg_body.originalLockHld}], "
            f"累计锁定[{msg_body.totalLockHld}], "
            f"累计解锁[{msg_body.totalUnlockHld}], "
            f"当前总持仓[{msg_body.sumHld}], "
            f"当前可卖[{msg_body.sellAvlHld}], "
            f"当前可转换付出[{msg_body.trsfOutAvlHld}], "
            f"当前可锁定[{msg_body.lockAvlHld}]")

        return 0

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
        print(f">>> 查询到融资融券余券信息: "
            f"index[{cursor.seqNo}], "
            f"isEnd[{'Y' if cursor.isEnd else 'N'}], "
            f"客户代码[{msg_body.custId.decode()}], "
            f"证券账户代码[{msg_body.invAcctId.decode()}], "
            f"证券代码[{msg_body.securityId.decode()}], "
            f"市场代码[{msg_body.mktId}], "
            f"日初余券数量[{msg_body.originExcessStockQty}], "
            f"余券数量[{msg_body.excessStockTotalQty}], "
            f"余券已划转数量[{msg_body.excessStockUncomeTrsfQty}], "
            f"余券可划转数量[{msg_body.excessStockTrsfAbleQty}]")

        return 0

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
        print(f">>> 查询到融资融券合约流水信息: "
            f"index[{cursor.seqNo}], "
            f"isEnd[{'Y' if cursor.isEnd else 'N'}], "
            f"合约编号[{msg_body.debtId}], "
            f"资金账户代码[{msg_body.cashAcctId.decode()}], "
            f"股东账户代码[{msg_body.invAcctId.decode()}], "
            f"证券代码[{msg_body.securityId.decode()}], "
            f"市场代码[{msg_body.mktId}], "
            f"负债类型[{msg_body.debtType}], "
            f"流水类型[{msg_body.journalType}], "
            f"强制标志[{msg_body.mandatoryFlag}], "
            f"同一融资融券合约的负债流水的顺序号[{msg_body.seqNo}], "
            f"发生金额[{msg_body.occurAmt}], "
            f"发生费用[{msg_body.occurFee}], "
            f"发生利息[{msg_body.occurInterest}], "
            f"发生证券数量[{msg_body.occurQty}], "
            f"后余证券数量[{msg_body.postQty}], "
            f"后余金额[{msg_body.postAmt}], "
            f"后余费用[{msg_body.postFee}], "
            f"后余利息[{msg_body.postInterest}], "
            f"融券合约流水的理论发生金额[{msg_body.shortSellTheoryOccurAmt}], "
            f"归还息费时使用融券卖出所得抵扣的金额[{msg_body.useShortSellGainedAmt}], "
            f"委托日期[{msg_body.ordDate}], "
            f"委托时间[{msg_body.ordTime}]")

        return 0

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
        print(f">>> 查询到融资融券息费利率信息: "
            f"index[{cursor.seqNo}], "
            f"isEnd[{'Y' if cursor.isEnd else 'N'}], "
            f"客户代码[{msg_body.custId.decode()}], "
            f"证券代码[{msg_body.securityId.decode()}], "
            f"市场代码[{msg_body.mktId}], "
            f"证券类别[{msg_body.securityType}], "
            f"证券子类别[{msg_body.subSecurityType}], "
            f"买卖类型[{msg_body.bsType}], "
            f"费用标识[{msg_body.feeType}], "
            f"币种[{msg_body.currType}], "
            f"计算模式[{msg_body.calcFeeMode}], "
            f"费率[{msg_body.feeRate}], "
            f"最低费用[{msg_body.minFee}], "
            f"最高费用[{msg_body.maxFee}]")

        return 0

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
        print(f">>> 查询到融资融券可充抵保证金证券及融资融券标的信息: "
            f"index[{cursor.seqNo}], "
            f"isEnd[{'Y' if cursor.isEnd else 'N'}], "
            f"客户代码[{msg_body.custId.decode()}], "
            f"证券代码[{msg_body.securityId.decode()}], "
            f"市场代码[{msg_body.mktId}], "
            f"产品类型[{msg_body.productType}], "
            f"证券类型[{msg_body.securityType}], "
            f"证券子类型[{msg_body.subSecurityType}], "
            f"是否为融资融券可充抵保证金证券[{msg_body.isCrdCollateral}], "
            f"是否为融资标的[{msg_body.isCrdMarginTradeUnderlying}], "
            f"是否为融券标的[{msg_body.isCrdShortSellUnderlying}], "
            f"融资融券可充抵保证金证券的交易状态[{msg_body.isCrdCollateralTradable}], "
            f"是否已为个人设置融资融券担保品参数[{msg_body.isIndividualCollateral}], "
            f"是否已为个人设置融资融券标的参数[{msg_body.isIndividualUnderlying}], "
            f"可充抵保证金折算率[{msg_body.collateralRatio}], "
            f"融资买入保证金比例[{msg_body.marginBuyRatio}], "
            f"融券卖出保证金比例[{msg_body.shortSellRatio}]")

        return 0
