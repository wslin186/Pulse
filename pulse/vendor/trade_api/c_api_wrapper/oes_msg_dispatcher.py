# -*- coding: utf-8 -*-
"""
capi消息分发相关
"""

from ctypes import (
    POINTER, _Pointer, cast, c_void_p
)

from typing import (
    Any, Callable, Dict, List, Tuple, Optional
)

from functools import (
    partial
)

from vendor.trade_api.model import (
    # spk_util.py
    CFuncPointer, memcpy, SMsgHeadT, VOID_NULLPTR,
    OesAsyncApiChannelT, OesAsyncApiChannelCfgT,

    # oes_base_constants.py

    # oes_base_model_credit.py
    OesCrdCreditAssetItemT,
    OesCrdDebtContractItemT, OesCrdDebtJournalItemT, OesCrdExcessStockItemT,
    OesCrdSecurityDebtStatsItemT, OesCrdUnderlyingInfoItemT,

    # oes_base_model_option_.py
    OesOptExerciseAssignItemT, OesOptUnderlyingHoldingItemT, OesOptionItemT,

    # oes_base_model.py
    OesOrdItemT, OesTrdItemT, OesStkHoldingItemT,
    OesCashAssetItemT, OesEtfItemT, OesFundTransferSerialItemT,
    OesStockItemT, OesIssueItemT, OesLotWinningItemT,
    OesCommissionRateItemT, OesCrdCashRepayItemT,


    # oes_qry_packets.py
    OesCustItemT, OesInvAcctItemT, OesMarketStateItemT,
    OesEtfComponentItemT, OesCrdInterestRateItemT, OesQryCursorT,

    # oes_qry_packets_credit.py
    OesCrdCashPositionItemT, OesCrdSecurityPositionItemT,

    # oes_qry_packets_option.py
    OesOptHoldingItemT, OesOptPositionLimitItemT, OesOptPurchaseLimitItemT,

    # oes_packets.py
    eOesMsgTypeT, OesRspMsgBodyT, OesNotifyInfoItemT,
)

from vendor.trade_api.oes_spi import (
    OesClientSpi
)

from .oes_func_loader import (
    F_OESAPI_ASYNC_ON_QRY_MSG_T,
    F_OESAPI_ASYNC_ON_RPT_MSG_T,
    F_OESAPI_ASYNC_ON_CONNECT_T,
    F_OESAPI_ASYNC_ON_DISCONNECT_T,
    COesApiFuncLoader, log_error
)


# ===================================================================
# OES消息ID对应回调函数的派发规则定义
# dict字典说明:
# - {消息ID, Tuple[]}
# - KEY  : 消息ID
# - VALUE: tuple元组
#   - tuple元组说明:
#     - 0号元素: OES回报消息结构体
#     - 1号元素: OES回报的回调函数 (@note 参数5:OesQryCursorT 仅适用于查询相关定义)
# ===================================================================

# 消息id对回调函数的派发规则
_OES_MSG_ID_TO_CALLBACK: Dict[
    int,
    Tuple[Any, Callable[[OesAsyncApiChannelT, OesClientSpi, SMsgHeadT, Any, OesQryCursorT, Any], Any]]
] = {
        # OES委托已生成 (已通过风控检查) @see OesOrdCnfmT
        eOesMsgTypeT.OESMSG_RPT_ORDER_INSERT: [
            OesRspMsgBodyT,
            lambda channel, spi, msg_head, rsp_msg, _, user_info:
                spi.on_order_insert(
                    channel,
                    msg_head,
                    rsp_msg.rptMsg.rptHead,
                    rsp_msg.rptMsg.rptBody.ordInsertRsp,
                    user_info)
        ],

        # OES业务拒绝 (未通过风控检查等) @see OesOrdRejectT
        eOesMsgTypeT.OESMSG_RPT_BUSINESS_REJECT: [
            OesRspMsgBodyT,
            lambda channel, spi, msg_head, rsp_msg, _, user_info:
                spi.on_order_reject(
                    channel,
                    msg_head,
                    rsp_msg.rptMsg.rptHead,
                    rsp_msg.rptMsg.rptBody.ordRejectRsp,
                    user_info)
        ],

        # 交易所委托回报 (包括交易所委托拒绝、委托确认和撤单完成通知) @see OesOrdCnfmT
        eOesMsgTypeT.OESMSG_RPT_ORDER_REPORT: [
            OesRspMsgBodyT,
            lambda channel, spi, msg_head, rsp_msg, _, user_info:
                spi.on_order_report(
                    channel,
                    msg_head,
                    rsp_msg.rptMsg.rptHead,
                    rsp_msg.rptMsg.rptBody.ordCnfm,
                    user_info)
        ],

        # 交易所成交回报 @see OesTrdCnfmT
        eOesMsgTypeT.OESMSG_RPT_TRADE_REPORT: [
            OesRspMsgBodyT,
            lambda channel, spi, msg_head, rsp_msg, _, user_info:
                spi.on_trade_report(
                    channel,
                    msg_head,
                    rsp_msg.rptMsg.rptHead,
                    rsp_msg.rptMsg.rptBody.trdCnfm,
                    user_info)
        ],

        # 资金变动信息 @see OesCashAssetItemT
        eOesMsgTypeT.OESMSG_RPT_CASH_ASSET_VARIATION: [
            OesRspMsgBodyT,
            lambda channel, spi, msg_head, rsp_msg, _, user_info:
                spi.on_cash_asset_variation(
                    channel,
                    msg_head,
                    rsp_msg.rptMsg.rptHead,
                    rsp_msg.rptMsg.rptBody.cashAssetRpt,
                    user_info)
        ],

        # 持仓变动信息 (股票) @see OesStkHoldingItemT
        eOesMsgTypeT.OESMSG_RPT_STOCK_HOLDING_VARIATION: [
            OesRspMsgBodyT,
            lambda channel, spi, msg_head, rsp_msg, _, user_info:
                spi.on_stock_holding_variation(
                    channel,
                    msg_head,
                    rsp_msg.rptMsg.rptHead,
                    rsp_msg.rptMsg.rptBody.stkHoldingRpt,
                    user_info)
        ],

        # 期权持仓变动信息 @see OesOptHoldingReportT
        eOesMsgTypeT.OESMSG_RPT_OPTION_HOLDING_VARIATION: [
            OesRspMsgBodyT,
            lambda channel, spi, msg_head, rsp_msg, _, user_info:
                spi.on_option_holding_variation(
                    channel,
                    msg_head,
                    rsp_msg.rptMsg.rptHead,
                    rsp_msg.rptMsg.rptBody.optHoldingRpt,
                    user_info)
        ],

        # 期权标的持仓变动信息 @see OesOptUnderlyingHoldingReportT
        eOesMsgTypeT.OESMSG_RPT_OPTION_UNDERLYING_HOLDING_VARIATION: [
            OesRspMsgBodyT,
            lambda channel, spi, msg_head, rsp_msg, _, user_info:
                spi.on_option_underlying_holding_variation(
                    channel,
                    msg_head,
                    rsp_msg.rptMsg.rptHead,
                    rsp_msg.rptMsg.rptBody.optUnderlyingHoldingRpt,
                    user_info)
        ],

        # 期权账户结算单确认回报 @see OesOptSettlementConfirmReportT
        eOesMsgTypeT.OESMSG_RPT_OPTION_SETTLEMENT_CONFIRMED: [
            OesRspMsgBodyT,
            lambda channel, spi, msg_head, rsp_msg, _, user_info:
                spi.on_option_settlement_confirmed_rpt(
                    channel,
                    msg_head,
                    rsp_msg.rptMsg.rptHead,
                    rsp_msg.rptMsg.rptBody.optSettlementConfirmRpt,
                    user_info)
        ],

        # 出入金委托响应-业务拒绝 @see OesFundTrsfRejectT
        eOesMsgTypeT.OESMSG_RPT_FUND_TRSF_REJECT: [
            OesRspMsgBodyT,
            lambda channel, spi, msg_head, rsp_msg, _, user_info:
                spi.on_fund_trsf_reject(
                    channel,
                    msg_head,
                    rsp_msg.rptMsg.rptHead,
                    rsp_msg.rptMsg.rptBody.fundTrsfRejectRsp,
                    user_info)
        ],

        # 出入金委托执行报告 @see OesFundTrsfReportT
        eOesMsgTypeT.OESMSG_RPT_FUND_TRSF_REPORT: [
            OesRspMsgBodyT,
            lambda channel, spi, msg_head, rsp_msg, _, user_info:
                spi.on_fund_trsf_report(
                    channel,
                    msg_head,
                    rsp_msg.rptMsg.rptHead,
                    rsp_msg.rptMsg.rptBody.fundTrsfCnfm,
                    user_info)
        ],

        # 融资融券直接还款委托执行报告 @see OesCrdCashRepayReportT
        eOesMsgTypeT.OESMSG_RPT_CREDIT_CASH_REPAY_REPORT: [
            OesRspMsgBodyT,
            lambda channel, spi, msg_head, rsp_msg, _, user_info:
                spi.on_credit_cash_repay_report(
                    channel,
                    msg_head,
                    rsp_msg.rptMsg.rptHead,
                    rsp_msg.rptMsg.rptBody.crdDebtCashRepayRpt,
                    user_info)
        ],

        # 融资融券合约变动信息 @see OesCrdDebtContractReportT
        eOesMsgTypeT.OESMSG_RPT_CREDIT_DEBT_CONTRACT_VARIATION: [
            OesRspMsgBodyT,
            lambda channel, spi, msg_head, rsp_msg, _, user_info:
                spi.on_credit_debt_contract_variation(
                    channel,
                    msg_head,
                    rsp_msg.rptMsg.rptHead,
                    rsp_msg.rptMsg.rptBody.crdDebtContractRpt,
                    user_info)
        ],

        # 融资融券合约流水信息 @see OesCrdDebtJournalReportT
        eOesMsgTypeT.OESMSG_RPT_CREDIT_DEBT_JOURNAL: [
            OesRspMsgBodyT,
            lambda channel, spi, msg_head, rsp_msg, _, user_info:
                spi.on_credit_debt_journal_report(
                    channel,
                    msg_head,
                    rsp_msg.rptMsg.rptHead,
                    rsp_msg.rptMsg.rptBody.crdDebtJournalRpt,
                    user_info)
        ],

        # 回报同步的应答消息 @see OesReportSynchronizationRspT
        eOesMsgTypeT.OESMSG_RPT_REPORT_SYNCHRONIZATION: [
            OesRspMsgBodyT,
            lambda channel, spi, msg_head, rsp_msg, _, user_info:
                spi.on_report_synchronization(
                    channel,
                    msg_head,
                    rsp_msg.rptMsg.rptHead,
                    rsp_msg.reportSynchronizationRsp,
                    user_info)
        ],

        # 市场状态信息 @see OesMarketStateInfoT
        eOesMsgTypeT.OESMSG_RPT_MARKET_STATE: [
            OesRspMsgBodyT,
            lambda channel, spi, msg_head, rsp_msg, _, user_info:
                spi.on_market_state(
                    channel,
                    msg_head,
                    rsp_msg.rptMsg.rptHead,
                    rsp_msg.mktStateRpt,
                    user_info)
        ],

        # 通知消息 @see OesNotifyInfoReportT
        eOesMsgTypeT.OESMSG_RPT_NOTIFY_INFO: [
            OesRspMsgBodyT,
            lambda channel, spi, msg_head, rsp_msg, _, user_info:
                spi.on_notify_report(
                    channel,
                    msg_head,
                    rsp_msg.rptMsg.rptHead,
                    rsp_msg.rptMsg.rptBody.notifyInfoRpt,
                    user_info)
        ],

        # 心跳消息
        eOesMsgTypeT.OESMSG_SESS_HEARTBEAT: [
            None,
            lambda channel, spi, msg_head, rsp_msg, _, user_info:
                spi.on_heart_beat(
                    channel,
                    msg_head,
                    rsp_msg,
                    user_info)
        ],

        # 测试请求消息
        eOesMsgTypeT.OESMSG_SESS_TEST_REQUEST: [
            OesRspMsgBodyT,
            lambda channel, spi, msg_head, rsp_msg, _, user_info:
                spi.on_test_request_rsp(
                    channel,
                    msg_head,
                    rsp_msg,
                    user_info)
        ],

        # 登录密码修改的应答消息 @see OesChangePasswordRspT
        eOesMsgTypeT.OESMSG_NONTRD_CHANGE_PASSWORD: [
            OesRspMsgBodyT,
            lambda channel, spi, msg_head, rsp_msg, _, user_info:
                spi.on_change_password_rsp(
                    channel,
                    msg_head,
                    rsp_msg,
                    user_info)
        ],

        # 结算单确认的应答消息 @see OesOptSettlementConfirmRspT
        eOesMsgTypeT.OESMSG_NONTRD_OPT_CONFIRM_SETTLEMENT: [
            OesRspMsgBodyT,
            lambda channel, spi, msg_head, rsp_msg, _, user_info:
                spi.on_option_confirm_settlement_rsp(
                    channel,
                    msg_head,
                    rsp_msg,
                    user_info)
        ],
        # -------------------------


        # ===================================================================
        # 查询回报相关消息定义
        # ===================================================================

        # 查询委托信息 @see OesOrdItemT
        eOesMsgTypeT.OESMSG_QRYMSG_ORD: [
            OesOrdItemT,
            lambda channel, spi, msg_head, msg_body, qry_cursor, user_info:
                spi.on_query_order(
                    channel,
                    msg_head,
                    msg_body,
                    qry_cursor,
                    user_info)
        ],

        # 查询成交信息 @see OesTrdItemT
        eOesMsgTypeT.OESMSG_QRYMSG_TRD: [
            OesTrdItemT,
            lambda channel, spi, msg_head, msg_body, qry_cursor, user_info:
                spi.on_query_trade(
                    channel,
                    msg_head,
                    msg_body,
                    qry_cursor,
                    user_info)
        ],

        # 查询客户资金信息 @see OesCashAssetItemT
        eOesMsgTypeT.OESMSG_QRYMSG_CASH_ASSET: [
            OesCashAssetItemT,
            lambda channel, spi, msg_head, msg_body, qry_cursor, user_info:
                spi.on_query_cash_asset(
                    channel,
                    msg_head,
                    msg_body,
                    qry_cursor,
                    user_info)
        ],

        # 查询股票持仓信息 (含信用持仓处理) @see OesStkHoldingItemT
        eOesMsgTypeT.OESMSG_QRYMSG_STK_HLD: [
            OesStkHoldingItemT,
            lambda channel, spi, msg_head, msg_body, qry_cursor, user_info:
                spi.on_query_crd_holding(
                    channel,
                    msg_head,
                    msg_body,
                    qry_cursor,
                    user_info
                ) if msg_body.isCreditHolding else
                spi.on_query_stk_holding(
                    channel,
                    msg_head,
                    msg_body,
                    qry_cursor,
                    user_info),
        ],

        # 查询新股配号、中签信息 @see OesLotWinningItemT
        eOesMsgTypeT.OESMSG_QRYMSG_LOT_WINNING: [
            OesLotWinningItemT,
            lambda channel, spi, msg_head, msg_body, qry_cursor, user_info:
                spi.on_query_lot_winning(
                    channel,
                    msg_head,
                    msg_body,
                    qry_cursor,
                    user_info)
        ],

        # 查询客户信息 @see OesCustItemT
        eOesMsgTypeT.OESMSG_QRYMSG_CUST: [
            OesCustItemT,
            lambda channel, spi, msg_head, msg_body, qry_cursor, user_info:
                spi.on_query_cust_info(
                    channel,
                    msg_head,
                    msg_body,
                    qry_cursor,
                    user_info)
        ],

        # 查询证券账户信息 @see OesInvAcctItemT
        eOesMsgTypeT.OESMSG_QRYMSG_INV_ACCT: [
            OesInvAcctItemT,
            lambda channel, spi, msg_head, msg_body, qry_cursor, user_info:
                spi.on_query_inv_acct(
                    channel,
                    msg_head,
                    msg_body,
                    qry_cursor,
                    user_info)
        ],

        # 查询客户佣金信息 @see OesCommissionRateItemT
        eOesMsgTypeT.OESMSG_QRYMSG_COMMISSION_RATE: [
            OesCommissionRateItemT,
            lambda channel, spi, msg_head, msg_body, qry_cursor, user_info:
                spi.on_query_commission_rate(
                    channel,
                    msg_head,
                    msg_body,
                    qry_cursor,
                    user_info)
        ],

        # 查询出入金信息 @see OesFundTransferSerialItemT
        eOesMsgTypeT.OESMSG_QRYMSG_FUND_TRSF: [
            OesFundTransferSerialItemT,
            lambda channel, spi, msg_head, msg_body, qry_cursor, user_info:
                spi.on_query_fund_transfer_serial(
                    channel,
                    msg_head,
                    msg_body,
                    qry_cursor,
                    user_info)
        ],

        # 查询证券发行信息 @see OesIssueItemT
        eOesMsgTypeT.OESMSG_QRYMSG_ISSUE: [
            OesIssueItemT,
            lambda channel, spi, msg_head, msg_body, qry_cursor, user_info:
                spi.on_query_issue(
                    channel,
                    msg_head,
                    msg_body,
                    qry_cursor,
                    user_info)
        ],

        # 查询现货产品信息 @see OesStockItemT
        eOesMsgTypeT.OESMSG_QRYMSG_STOCK: [
            OesStockItemT,
            lambda channel, spi, msg_head, msg_body, qry_cursor, user_info:
                spi.on_query_stock(
                    channel,
                    msg_head,
                    msg_body,
                    qry_cursor,
                    user_info)
        ],

        # 查询ETF申赎产品信息 @see OesEtfItemT
        eOesMsgTypeT.OESMSG_QRYMSG_ETF: [
            OesEtfItemT,
            lambda channel, spi, msg_head, msg_body, qry_cursor, user_info:
                spi.on_query_etf(
                    channel,
                    msg_head,
                    msg_body,
                    qry_cursor,
                    user_info)
        ],

        # 查询ETF成份证券信息 @see OesEtfComponentItemT
        eOesMsgTypeT.OESMSG_QRYMSG_ETF_COMPONENT: [
            OesEtfComponentItemT,
            lambda channel, spi, msg_head, msg_body, qry_cursor, user_info:
                spi.on_query_etf_component(
                    channel,
                    msg_head,
                    msg_body,
                    qry_cursor,
                    user_info)
        ],

        # 查询市场状态 @see OesMarketStateItemT
        eOesMsgTypeT.OESMSG_QRYMSG_MARKET_STATE: [
            OesMarketStateItemT,
            lambda channel, spi, msg_head, msg_body, qry_cursor, user_info:
                spi.on_query_market_state(
                    channel,
                    msg_head,
                    msg_body,
                    qry_cursor,
                    user_info)
        ],

        # 查询通知消息 @see OesNotifyInfoItemT
        eOesMsgTypeT.OESMSG_QRYMSG_NOTIFY_INFO: [
            OesNotifyInfoItemT,
            lambda channel, spi, msg_head, msg_body, qry_cursor, user_info:
                spi.on_query_notify_info(
                    channel,
                    msg_head,
                    msg_body,
                    qry_cursor,
                    user_info)
        ],

        # 查询期权产品信息 @see OesOptionItemT
        eOesMsgTypeT.OESMSG_QRYMSG_OPTION: [
            OesOptionItemT,
            lambda channel, spi, msg_head, msg_body, qry_cursor, user_info:
                spi.on_query_option(
                    channel,
                    msg_head,
                    msg_body,
                    qry_cursor,
                    user_info)
        ],

        # 查询期权持仓信息 @see OesOptHoldingItemT
        eOesMsgTypeT.OESMSG_QRYMSG_OPT_HLD: [
            OesOptHoldingItemT,
            lambda channel, spi, msg_head, msg_body, qry_cursor, user_info:
                spi.on_query_opt_holding(
                    channel,
                    msg_head,
                    msg_body,
                    qry_cursor,
                    user_info)
        ],

        # 查询期权标的持仓信息 @see OesOptUnderlyingHoldingItemT
        eOesMsgTypeT.OESMSG_QRYMSG_OPT_UNDERLYING_HLD: [
            OesOptUnderlyingHoldingItemT,
            lambda channel, spi, msg_head, msg_body, qry_cursor, user_info:
                spi.on_query_opt_underlying_holding(
                    channel,
                    msg_head,
                    msg_body,
                    qry_cursor,
                    user_info)
        ],

        # 查询期权限仓额度信息 @see OesOptPositionLimitItemT
        eOesMsgTypeT.OESMSG_QRYMSG_OPT_POSITION_LIMIT: [
            OesOptPositionLimitItemT,
            lambda channel, spi, msg_head, msg_body, qry_cursor, user_info:
                spi.on_query_opt_position_limit(
                    channel,
                    msg_head,
                    msg_body,
                    qry_cursor,
                    user_info)
        ],

        # 查询期权限购额度信息 @see OesOptPurchaseLimitItemT
        eOesMsgTypeT.OESMSG_QRYMSG_OPT_PURCHASE_LIMIT: [
            OesOptPurchaseLimitItemT,
            lambda channel, spi, msg_head, msg_body, qry_cursor, user_info:
                spi.on_query_opt_purchase_limit(
                    channel,
                    msg_head,
                    msg_body,
                    qry_cursor,
                    user_info)
        ],

        # 查询期权行权指派信息 @see OesOptExerciseAssignItemT
        eOesMsgTypeT.OESMSG_QRYMSG_OPT_EXERCISE_ASSIGN: [
            OesOptExerciseAssignItemT,
            lambda channel, spi, msg_head, msg_body, qry_cursor, user_info:
                spi.on_query_opt_exercise_assign(
                    channel,
                    msg_head,
                    msg_body,
                    qry_cursor,
                    user_info)
        ],

        # 查询信用资产信息 @see OesCrdCreditAssetItemT
        eOesMsgTypeT.OESMSG_QRYMSG_CRD_CREDIT_ASSET: [
            OesCrdCreditAssetItemT,
            lambda channel, spi, msg_head, msg_body, qry_cursor, user_info:
                spi.on_query_crd_credit_asset(
                    channel,
                    msg_head,
                    msg_body,
                    qry_cursor,
                    user_info)
        ],

        # 查询融资融券可充抵保证金证券及融资融券标的信息 @see OesCrdUnderlyingInfoItemT
        eOesMsgTypeT.OESMSG_QRYMSG_CRD_UNDERLYING_INFO: [
            OesCrdUnderlyingInfoItemT,
            lambda channel, spi, msg_head, msg_body, qry_cursor, user_info:
                spi.on_query_crd_underlying_info(
                    channel,
                    msg_head,
                    msg_body,
                    qry_cursor,
                    user_info)
        ],

        # 查询融资融券业务资金头寸信息 (可融资头寸信息) @see OesCrdCashPositionItemT
        eOesMsgTypeT.OESMSG_QRYMSG_CRD_CASH_POSITION: [
            OesCrdCashPositionItemT,
            lambda channel, spi, msg_head, msg_body, qry_cursor, user_info:
                spi.on_query_crd_cash_position(
                    channel,
                    msg_head,
                    msg_body,
                    qry_cursor,
                    user_info)
        ],

        # 查询融资融券业务证券头寸信息 (可融券头寸信息) @see OesCrdSecurityPositionItemT
        eOesMsgTypeT.OESMSG_QRYMSG_CRD_SECURITY_POSITION: [
            OesCrdSecurityPositionItemT,
            lambda channel, spi, msg_head, msg_body, qry_cursor, user_info:
                spi.on_query_crd_security_position(
                    channel,
                    msg_head,
                    msg_body,
                    qry_cursor,
                    user_info)
        ],

        # 查询信用业务股票持仓信息 @see OesStkHoldingItemT
        # 同 eOesMsgTypeT.OESMSG_QRYMSG_STK_HLD 分支处理

        # 查询融资融券合约信息 @see OesCrdDebtContractItemT
        eOesMsgTypeT.OESMSG_QRYMSG_CRD_DEBT_CONTRACT: [
            OesCrdDebtContractItemT,
            lambda channel, spi, msg_head, msg_body, qry_cursor, user_info:
                spi.on_query_crd_debt_contract(
                    channel,
                    msg_head,
                    msg_body,
                    qry_cursor,
                    user_info)
        ],

        # 查询融资融券合约流水信息 (仅当日流水) @see OesCrdDebtJournalItemT
        eOesMsgTypeT.OESMSG_QRYMSG_CRD_DEBT_JOURNAL: [
            OesCrdDebtJournalItemT,
            lambda channel, spi, msg_head, msg_body, qry_cursor, user_info:
                spi.on_query_crd_debt_journal(
                    channel,
                    msg_head,
                    msg_body,
                    qry_cursor,
                    user_info)
        ],

        # 查询融资融券业务直接还款信息 @see OesCrdCashRepayItemT
        eOesMsgTypeT.OESMSG_QRYMSG_CRD_CASH_REPAY_INFO: [
            OesCrdCashRepayItemT,
            lambda channel, spi, msg_head, msg_body, qry_cursor, user_info:
                spi.on_query_crd_cash_repay_order(
                    channel,
                    msg_head,
                    msg_body,
                    qry_cursor,
                    user_info)
        ],

        # 查询客户单证券融资融券负债统计信息 @see OesCrdSecurityDebtStatsItemT
        eOesMsgTypeT.OESMSG_QRYMSG_CRD_CUST_SECU_DEBT_STATS: [
            OesCrdSecurityDebtStatsItemT,
            lambda channel, spi, msg_head, msg_body, qry_cursor, user_info:
                spi.on_query_crd_security_debt_stats(
                    channel,
                    msg_head,
                    msg_body,
                    qry_cursor,
                    user_info)
        ],

        # 查询融资融券业务余券信息 @see OesCrdExcessStockItemT
        eOesMsgTypeT.OESMSG_QRYMSG_CRD_EXCESS_STOCK: [
            OesCrdExcessStockItemT,
            lambda channel, spi, msg_head, msg_body, qry_cursor, user_info:
                spi.on_query_crd_excess_stock(
                    channel,
                    msg_head,
                    msg_body,
                    qry_cursor,
                    user_info)
        ],

        # 查询融资融券息费利率 @see OesCrdInterestRateItemT
        eOesMsgTypeT.OESMSG_QRYMSG_CRD_INTEREST_RATE: [
            OesCrdInterestRateItemT,
            lambda channel, spi, msg_head, msg_body, qry_cursor, user_info:
                spi.on_query_crd_interest_rate(
                    channel,
                    msg_head,
                    msg_body,
                    qry_cursor,
                    user_info)
        ],
        # -------------------------
}


class OesMsgDispatcher:
    """
    python对c_oes_api回调函数的转换类
    """

    def __init__(self, spi: OesClientSpi, copy_args: bool) -> None:
        """
        Args:
            spi (OesClientSpi): [回调处理类实例]
            copy_args (bool, optional): [capi回调时是否复制参数]. Defaults to True.

        Raises:
            Exception: [参数spi类型错误]
        """
        if not isinstance(spi, OesClientSpi):
            raise Exception(f'spi参数错误:{spi}:{type(spi)}')

        self._spi: OesClientSpi = spi
        self._copy_args = copy_args

        # python有垃圾回收，传递给capi的非实时调用回调需要增加引用防止自动回收
        self._refs: List[CFuncPointer] = []

    def get_spi(self) -> OesClientSpi:
        return self._spi

    def release(self) -> None:
        """
        释放额外增添引用的回调
        """
        self._refs = []

    def _on_connect(self, p_channel: _Pointer, p_params: c_void_p,
            partial_user_info: Any, partial_is_ord_channel: bool) -> int:
        """
        异步API线程连接或重新连接完成后的回调函数
        - 回调函数运行在异步API线程下

        Args:
            p_channel (_Pointer[OesAsyncApiChannelT]): [连接通道]
            p_params (c_void_p, None): [CAPI 用户回调参数, 取值固定为空; 回调参数通过<partial_user_info>在Python层面进行传递]
            partial_user_info (Any, None): [用户实际回调参数, 由偏函数传入]
            partial_is_ord_channel (bool): [是否是委托通道]

        Returns:
            int: [
                    =0 等于0, 成功
                    <0 小于0, 处理失败, 异步线程将中止运行
                    >0 大于0, 处理失败, 将重建连接并继续尝试执行
                 ]
        """
        if partial_is_ord_channel:
            on_connect_callback = self._spi.on_ord_connect
        else:
            on_connect_callback = self._spi.on_rpt_connect

        try:
            ret: int = on_connect_callback(
                memcpy(p_channel.contents), partial_user_info)

            if ret < 0:
                # 返回小于0的值, 处理失败, 异步API将中止运行
                return ret
            elif ret == 0:
                # 若返回0, 表示已经处理成功
                return 0
            else:
                # 返回大于0的值, 执行默认的连接完成后处理
                # - 对于委托通道, 将输出连接成功的日志信息
                # - 对于回报通道, 将执行默认的回报订阅处理
                return COesApiFuncLoader().c_oes_async_api_default_on_connect(
                    p_channel, VOID_NULLPTR)

        except Exception as err:
            channel_cfg: OesAsyncApiChannelCfgT = \
                p_channel.contents.pChannelCfg.contents  # type: ignore

            log_error("调用通道spi.on_connect回调函数时异常! channelType[{}], "
                      "error_msg[{}]".format(channel_cfg.channelType, err))
            return -1

    def on_ord_connect(self, user_info: Any) -> CFuncPointer:
        """
        对spi.on_ord_connect进行包装，返回符合capi类型的委托通道连接成功回调函数

        Args:
            user_info (Any, None): [用户回调参数]
        Returns:
            CFuncPointer: [传递给capi的委托通道连接成功回调函数]
        """
        func: CFuncPointer = F_OESAPI_ASYNC_ON_CONNECT_T(
            partial(self._on_connect,
                partial_user_info=user_info,
                partial_is_ord_channel = True))
        # 回调异步运行在回报线程中，因此需要增加引用，防止被自动垃圾回收
        self._refs.append(func)
        return func

    def on_rpt_connect(self, user_info: Any) -> CFuncPointer:
        """
        对spi.on_rpt_connect进行包装，返回符合capi类型的回报通道连接成功回调函数

        Args:
            user_info (Any): [用户回调参数]
        Returns:
            CFuncPointer: [传递给capi的回报通道连接成功回调函数]
        """
        func: CFuncPointer = F_OESAPI_ASYNC_ON_CONNECT_T(
            partial(self._on_connect,
                partial_user_info=user_info,
                partial_is_ord_channel = False))
        # 回调异步运行在回报线程中，因此需要增加引用，防止被自动垃圾回收
        self._refs.append(func)
        return func

    def _on_connect_failed(self, p_channel: _Pointer, p_params: c_void_p,
            partial_user_info: Any, partial_is_ord_channel: bool) -> int:
        """
        异步API线程连接断开后的回调函数
        - 仅用于通知客户端连接已经断开, 无需做特殊处理, 异步线程会自动尝试重建连接

        Args:
            p_channel (_Pointer[OesAsyncApiChannelT]): [连接通道]
            p_params (c_void_p, None): [CAPI 用户回调参数, 取值固定为空; 回调参数通过<partial_user_info>在Python层面进行传递]
            partial_user_info (Any, None): [用户实际回调参数, 由偏函数传入]
            partial_is_ord_channel (bool): [是否是委托通道]

        Returns:
            int: [
                    >=0 大于等于0, 异步线程将尝试重建连接并继续执行
                    <0  小于0, 异步线程将中止运行
                 ]
        """
        if partial_is_ord_channel:
            on_connect_failed_callback = self._spi.on_ord_connect_failed
        else:
            on_connect_failed_callback = self._spi.on_rpt_connect_failed

        try:
            return on_connect_failed_callback(
                memcpy(p_channel.contents), partial_user_info)

        except Exception as err:
            channel_cfg: OesAsyncApiChannelCfgT = \
                p_channel.contents.pChannelCfg.contents

            log_error("调用通道spi.on_connect_failed回调函数时异常! channelType[{}], "
                      "error_msg[{}]".format(channel_cfg.channelType, err))
            return -1

    def on_ord_connect_failed(self, user_info: Any) -> CFuncPointer:
        """
        对spi.on_connect_failed进行包装，返回行情订阅通道连接失败回调函数

        Args:
            user_info (Any): [用户回调参数]
        Returns:
            CFuncPointer: [传递给capi的通道连接失败回调函数]
        """

        func: CFuncPointer = F_OESAPI_ASYNC_ON_DISCONNECT_T(
            partial(self._on_connect_failed,
                partial_user_info=user_info,
                partial_is_ord_channel=True))
        # 回调异步运行在回报线程中，因此需要增加引用，防止被自动垃圾回收
        self._refs.append(func)
        return func

    def on_rpt_connect_failed(self, user_info: Any) -> CFuncPointer:
        """
        对spi.on_connect_failed进行包装，返回行情订阅通道连接失败回调函数

        Args:
            user_info (Any): [用户回调参数]
        Returns:
            CFuncPointer: [传递给capi的通道连接失败回调函数]
        """

        func: CFuncPointer = F_OESAPI_ASYNC_ON_DISCONNECT_T(
            partial(self._on_connect_failed,
                partial_user_info=user_info,
                partial_is_ord_channel=False))
        # 回调异步运行在回报线程中，因此需要增加引用，防止被自动垃圾回收
        self._refs.append(func)
        return func

    def _on_disconnect(self, p_channel: _Pointer, p_params: c_void_p,
            partial_user_info: Any, partial_is_ord_channel: bool) -> int:
        """
        异步API线程连接断开后的回调函数
        仅用于通知客户端连接已经断开, 无需做特殊处理, 异步线程会自动尝试重建连接
        - 回调函数运行在异步API线程下

        Args:
            p_channel (_Pointer[OesAsyncApiChannelT]): [连接通道]
            p_params (c_void_p, None): [CAPI 用户回调参数, 取值固定为空; 回调参数通过<partial_user_info>在Python层面进行传递]
            partial_user_info (Any, None): [用户实际回调参数, 由偏函数传入]
            partial_is_ord_channel (bool): [是否是委托通道]

        Returns:
            int: [
                    >=0 大于等于0, 异步线程将尝试重建连接并继续执行
                    <0  小于0, 异步线程将中止运行
                 ]
        """
        if partial_is_ord_channel:
            on_disconnect_callback = self._spi.on_ord_disconnect
        else:
            on_disconnect_callback = self._spi.on_rpt_disconnect

        try:
            return on_disconnect_callback(
                memcpy(p_channel.contents), partial_user_info)

        except Exception as err:
            channel_cfg: OesAsyncApiChannelCfgT = \
                p_channel.contents.pChannelCfg.contents

            log_error("调用通道spi.on_disconnect回调函数时异常! channelType[{}], "
                      "error_msg[{}]".format(channel_cfg.channelType, err))
            return -1

    def on_ord_disconnect(self, user_info: Any) -> CFuncPointer:
        """
        对spi.on_ord_disconnect进行包装，返回符合capi类型的委托通道连接断开回调函数

        Args:
            user_info (Any): [用户回调参数]
        Returns:
            CFuncPointer: [传递给capi的委托通道连接断开回调函数]
        """

        func: CFuncPointer = F_OESAPI_ASYNC_ON_DISCONNECT_T(
            partial(self._on_disconnect,
                partial_user_info=user_info,
                partial_is_ord_channel = True))
        # 回调异步运行在回报线程中，因此需要增加引用，防止被自动垃圾回收
        self._refs.append(func)
        return func

    def on_rpt_disconnect(self, user_info: Any) -> CFuncPointer:
        """
        对spi.on_rpt_disconnect进行包装，返回符合capi类型的回报通道连接断开回调函数

        Args:
            user_info (Any): [用户回调参数]
        Returns:
            CFuncPointer: [传递给capi的回报通道连接断开回调函数]
        """

        func: CFuncPointer = F_OESAPI_ASYNC_ON_DISCONNECT_T(
            partial(self._on_disconnect,
                partial_user_info=user_info,
                partial_is_ord_channel = False))
        # 回调异步运行在回报线程中，因此需要增加引用，防止被自动垃圾回收
        self._refs.append(func)
        return func

    def _handle_qry_msg(self, p_session: c_void_p, p_msg_head: _Pointer,
            p_msg_item: c_void_p, p_qry_cursor: c_void_p, p_params: c_void_p,
            partial_user_info: Any) -> int:
        """
        对查询的回报消息进行派发的回调函数 (适用于查询通道)
        - 运行在异步API线程下

        Args:
            p_session (c_void_p): [异步API会话信息]
            p_msg_head (_Pointer[SMsgHeadT]): [查询回报消息的消息头]
            p_msg_item (_Pointer[OesRspMsgBodyT]): [查询回报消息的数据条目]
            p_qry_cursor (_Pointer[OesRspMsgBodyT]): [查询定位的游标结构]
            p_params (c_void_p, None): [CAPI 用户回调参数, 取值固定为空; 回调参数通过<partial_user_info>在Python层面进行传递]
            partial_user_info (Any, None): [用户实际回调参数, 由偏函数传入]

        Returns:
            [0]: [成功]
        """
        msg_id: int = int(p_msg_head.contents.msgId)
        p_channel = COesApiFuncLoader().\
            c_oes_async_api_get_channel_by_session(p_session)

        tuple_callback = _OES_MSG_ID_TO_CALLBACK.get(msg_id)
        if not tuple_callback:
            log_error(f"Invalid message type! msgId[0x{msg_id:0x}]")
            return 0

        # 元组说明:
        # - 0号元素: OES查询回报消息结构体
        # - 1号元素: OES查询回报的回调函数
        e_oes_msg_type = tuple_callback[0]
        qry_callback: Optional[Callable] = tuple_callback[1]

        ret: int = -1
        try:
            if self._copy_args:
                ret = qry_callback(p_channel.contents, self._spi,
                    memcpy(p_msg_head.contents),
                    memcpy(cast(p_msg_item, POINTER(e_oes_msg_type)).contents),
                    memcpy(cast(p_qry_cursor, POINTER(OesQryCursorT)).contents),
                    partial_user_info)
            else:
                ret = qry_callback(p_channel.contents, self._spi,
                    p_msg_head.contents,
                    cast(p_msg_item, POINTER(e_oes_msg_type)).contents,
                    cast(p_qry_cursor, POINTER(OesQryCursorT)).contents,
                    partial_user_info)
        except Exception as err:
            log_error(f"调用消息msgId: {msg_id} 的回调函数时发生异常:{err}")

        return ret

    def handle_qry_msg(self, user_info: Any) -> CFuncPointer:
        """
        对self._handle_qry_msg，返回查询通道数据回调函数
        消息派发方式参考 _OES_MSG_ID_TO_CALLBACK

        Args:
            user_info (Any): [用户回调参数]
        Returns:
            CFuncPointer: [传递给capi的回报通道回报回调函数]
        """

        func: CFuncPointer = F_OESAPI_ASYNC_ON_QRY_MSG_T(
            partial(self._handle_qry_msg,
                partial_user_info=user_info))
        # 回调异步运行在回报线程中，因此需要增加引用，防止被自动垃圾回收
        self._refs.append(func)
        return func

    def _handle_report_msg(self, p_session: c_void_p, p_msg_head: _Pointer,
            p_msg_item: _Pointer, p_params: c_void_p, partial_user_info: Any) -> int:
        """
        对接收到的消息进行派发的回调函数 (适用于回报通道)
        - 运行在异步API线程下

        Args:
            p_session (c_void_p): [异步API会话信息]
            p_msg_head (_Pointer[SMsgHeadT]): [回报消息的消息头]
            p_msg_item (_Pointer[OesRspMsgBodyT]): [回报消息的数据条目]
            p_params (c_void_p, None): [CAPI 用户回调参数, 取值固定为空; 回调参数通过<partial_user_info>在Python层面进行传递]
            partial_user_info (Any, None): [用户实际回调参数, 由偏函数传入]

        Returns:
            [0]: [成功]
        """

        msg_id: int = int(p_msg_head.contents.msgId)
        p_channel = COesApiFuncLoader().\
            c_oes_async_api_get_channel_by_session(p_session)

        tuple_callback = _OES_MSG_ID_TO_CALLBACK.get(msg_id)
        if not tuple_callback:
            log_error(f"Invalid message type! msgId[0x{msg_id:0x}]")
            return 0

        # 元组说明:
        # - 0号元素: OES查询回报消息结构体
        # - 1号元素: OES查询回报的回调函数
        e_oes_msg_type = tuple_callback[0]
        callback: Optional[Callable] = tuple_callback[1]

        ret: int = -1
        try:
            if self._copy_args:
                ret = callback(p_channel.contents, self._spi,
                    memcpy(p_msg_head.contents),
                    memcpy(p_msg_item.contents),
                    OesQryCursorT(),     # 无实际意义
                    partial_user_info)
            else:
                ret = callback(p_channel.contents, self._spi,
                    p_msg_head.contents,
                    p_msg_item.contents,
                    OesQryCursorT(),     # 无实际意义
                    partial_user_info)
        except Exception as err:
            log_error(f"调用消息msgId: {msg_id} 的回调函数时发生异常:{err}")

        return ret

    def handle_report_msg(self, user_info: Any) -> CFuncPointer:
        """
        对self._handle_report_msg进行包装，返回回报的回调函数
        - @note 回报通道或委托通道
        - @note 消息派发方式参考 _OES_MSG_ID_TO_CALLBACK

        Args:
            user_info (Any): [用户回调参数]
        Returns:
            CFuncPointer: [传递给capi的回报的回调函数]
        """

        func: CFuncPointer = F_OESAPI_ASYNC_ON_RPT_MSG_T(
            partial(self._handle_report_msg, partial_user_info=user_info))
        # 回调异步运行在回报线程中，因此需要增加引用，防止被自动垃圾回收
        self._refs.append(func)
        return func
