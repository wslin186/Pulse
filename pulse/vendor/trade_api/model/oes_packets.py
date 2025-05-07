# -*- coding: utf-8 -*-
""" OES消息包相关结构体"""

from ctypes import c_char, c_uint8, c_int8, c_int16, c_int32, c_int64, Structure, Union

from .oes_base_constants import (
    # spk_util.py
    STimespec32T, UnionForUserInfo,

    OES_CLIENT_NAME_MAX_LEN,
    OES_PWD_MAX_LEN,
    OES_CUST_ID_MAX_LEN,
    OES_SECURITY_ID_MAX_LEN,
    OES_NOTIFY_CONTENT_MAX_LEN,
    OES_MAX_TEST_REQ_ID_LEN,
    OES_MAX_SENDING_TIME_LEN
)

from .oes_base_model import (
    OesCashAssetReportT, OesFundTrsfRejectT, OesFundTrsfReportT,
    OesOrdCnfmT, OesOrdRejectT, OesTrdCnfmT,
    OesStkHoldingReportT, OesCrdCashRepayReportT,
)

from .oes_base_model_option import (
    OesOptHoldingReportT, OesOptUnderlyingHoldingReportT,
    OesOptSettlementConfirmReportT,
#    OesOptSettlementConfirmReportT as OesOptSettlementConfirmRspT,
)


from .oes_base_model_credit import (
    OesCrdDebtContractReportT, OesCrdDebtJournalReportT
)

from .oes_qry_packets import (
    OesMarketStateInfoT,
)

OesOptSettlementConfirmRspT = OesOptSettlementConfirmReportT


# ===================================================================
# 消息代码及报文中的枚举类型定义
# ===================================================================

class eOesMsgTypeT:
    """
    通信消息的消息类型定义
    """
    # 交易类消息
    OESMSG_ORD_NEW_ORDER                    = 0x01  # 0x01/01  委托申报消息
    OESMSG_ORD_CANCEL_REQUEST               = 0x02  # 0x02/02  撤单请求消息
    OESMSG_ORD_BATCH_ORDERS                 = 0x03  # 0x03/03  批量委托消息

    OESMSG_ORD_CREDIT_REPAY                 = 0x04  # 0x04/04  融资融券负债归还请求消息
    OESMSG_ORD_CREDIT_CASH_REPAY            = 0x05  # 0x05/05  融资融券直接还款请求消息

    # 非交易类消息
    OESMSG_NONTRD_FUND_TRSF_REQ             = 0xC1  # 0xC1/193 出入金委托
    OESMSG_NONTRD_CHANGE_PASSWORD           = 0xC2  # 0xC2/194 修改客户端登录密码
    OESMSG_NONTRD_OPT_CONFIRM_SETTLEMENT    = 0xC3  # 0xC3/195 期权账户结算单确认

    # 执行报告类消息
    OESMSG_RPT_SERVICE_STATE                = 0x0E  # 0x0E/14  OES服务状态信息 (暂不支持订阅和推送)
    OESMSG_RPT_MARKET_STATE                 = 0x10  # 0x10/16  市场状态信息
    OESMSG_RPT_REPORT_SYNCHRONIZATION       = 0x11  # 0x11/17  回报同步的应答消息

    OESMSG_RPT_BUSINESS_REJECT              = 0x12  # 0x12/18  OES业务拒绝 (因未通过风控检查等原因而被OES拒绝)
    OESMSG_RPT_ORDER_INSERT                 = 0x13  # 0x13/19  OES委托已生成 (已通过风控检查)
    OESMSG_RPT_ORDER_REPORT                 = 0x14  # 0x14/20  交易所委托回报 (包括交易所委托拒绝、委托确认和撤单完成通知)
    OESMSG_RPT_TRADE_REPORT                 = 0x15  # 0x15/21  交易所成交回报

    OESMSG_RPT_FUND_TRSF_REJECT             = 0x16  # 0x16/22  出入金委托拒绝
    OESMSG_RPT_FUND_TRSF_REPORT             = 0x17  # 0x17/23  出入金委托执行报告

    OESMSG_RPT_CASH_ASSET_VARIATION         = 0x18  # 0x18/24  资金变动信息
    OESMSG_RPT_STOCK_HOLDING_VARIATION      = 0x19  # 0x19/25  持仓变动信息 (股票)
    OESMSG_RPT_OPTION_HOLDING_VARIATION     = 0x1A  # 0x1A/26  持仓变动信息 (期权)
    OESMSG_RPT_OPTION_UNDERLYING_HOLDING_VARIATION \
                                            = 0x1B  # 0x1B/27  期权标的持仓变动信息
    OESMSG_RPT_OPTION_SETTLEMENT_CONFIRMED  = 0x1C  # 0x1C/28  期权账户结算单确认消息
    OESMSG_RPT_NOTIFY_INFO                  = 0x1E  # 0x1E/30  OES通知消息
    OESMSG_RPT_CREDIT_CASH_REPAY_REPORT     = 0x20  # 0x20/32  融资融券直接还款委托执行报告
    OESMSG_RPT_CREDIT_DEBT_CONTRACT_VARIATION \
                                            = 0x21  # 0x21/33  融资融券合约变动信息
    OESMSG_RPT_CREDIT_DEBT_JOURNAL          = 0x22  # 0x22/34  融资融券合约流水信息

    # 查询类消息
    OESMSG_QRYMSG_OPT_HLD                   = 0x35  # 0x35/53  查询期权持仓信息
    OESMSG_QRYMSG_CUST                      = 0x36  # 0x36/54  查询客户信息
    OESMSG_QRYMSG_COMMISSION_RATE           = 0x38  # 0x38/56  查询客户佣金信息
    OESMSG_QRYMSG_FUND_TRSF                 = 0x39  # 0x39/57  查询出入金信息
    OESMSG_QRYMSG_ETF                       = 0x3B  # 0x3B/59  查询ETF申赎产品信息
    OESMSG_QRYMSG_OPTION                    = 0x3D  # 0x3D/61  查询期权产品信息
    OESMSG_QRYMSG_LOT_WINNING               = 0x3F  # 0x3F/63  查询新股配号、中签信息
    OESMSG_QRYMSG_TRADING_DAY               = 0x40  # 0x40/64  查询当前交易日
    OESMSG_QRYMSG_MARKET_STATE              = 0x41  # 0x41/65  查询市场状态
    OESMSG_QRYMSG_COUNTER_CASH              = 0x42  # 0x42/66  查询客户主柜资金信息
    OESMSG_QRYMSG_OPT_UNDERLYING_HLD        = 0x43  # 0x43/67  查询期权标的持仓信息
    OESMSG_QRYMSG_NOTIFY_INFO               = 0x44  # 0x44/68  查询通知消息
    OESMSG_QRYMSG_OPT_POSITION_LIMIT        = 0x45  # 0x45/69  查询期权限仓额度信息
    OESMSG_QRYMSG_OPT_PURCHASE_LIMIT        = 0x46  # 0x46/70  查询期权限购额度信息
    OESMSG_QRYMSG_BROKER_PARAMS             = 0x48  # 0x48/72  查询券商参数信息
    OESMSG_QRYMSG_COLOCATION_PEER_CASH      = 0x49  # 0x49/73  查询两地交易时对端结点的资金资产信息

    OESMSG_QRYMSG_INV_ACCT                  = 0x51  # 0x51/81  查询证券账户信息
    OESMSG_QRYMSG_ORD                       = 0x54  # 0x54/84  查询委托信息
    OESMSG_QRYMSG_TRD                       = 0x55  # 0x55/85  查询成交信息
    OESMSG_QRYMSG_OPT_EXERCISE_ASSIGN       = 0x56  # 0x56/86  查询期权行权指派信息
    OESMSG_QRYMSG_ISSUE                     = 0x57  # 0x57/87  查询证券发行信息
    OESMSG_QRYMSG_STOCK                     = 0x58  # 0x58/88  查询现货产品信息
    OESMSG_QRYMSG_ETF_COMPONENT             = 0x59  # 0x59/89  查询ETF成份证券信息
    OESMSG_QRYMSG_CLIENT_OVERVIEW           = 0x5A  # 0x5A/90  查询客户端总览信息
    OESMSG_QRYMSG_CASH_ASSET                = 0x5B  # 0x5B/91  查询客户资金信息
    OESMSG_QRYMSG_STK_HLD                   = 0x5C  # 0x5C/92  查询股票持仓信息

    OESMSG_QRYMSG_CRD_DEBT_CONTRACT         = 0x80  # 0x80/128 查询融资融券合约信息
    OESMSG_QRYMSG_CRD_CUST_SECU_DEBT_STATS  = 0x81  # 0x81/129 查询客户单证券融资融券负债统计信息
    OESMSG_QRYMSG_CRD_CREDIT_ASSET          = 0x82  # 0x82/130 查询信用资产信息
    OESMSG_QRYMSG_CRD_CASH_REPAY_INFO       = 0x83  # 0x83/131 查询融资融券业务直接还款信息
    OESMSG_QRYMSG_CRD_CASH_POSITION         = 0x84  # 0x84/132 查询融资融券业务资金头寸信息 (可融资头寸信息)
    OESMSG_QRYMSG_CRD_SECURITY_POSITION     = 0x85  # 0x85/133 查询融资融券业务证券头寸信息 (可融券头寸信息)
    OESMSG_QRYMSG_CRD_EXCESS_STOCK          = 0x86  # 0x86/134 查询融资融券业务余券信息
    OESMSG_QRYMSG_CRD_DEBT_JOURNAL          = 0x87  # 0x87/135 查询融资融券合约流水信息 (仅当日流水)
    OESMSG_QRYMSG_CRD_INTEREST_RATE         = 0x88  # 0x88/136 查询融资融券息费利率
    OESMSG_QRYMSG_CRD_UNDERLYING_INFO       = 0x89  # 0x89/137 查询融资融券可充抵保证金证券及融资融券标的信息
    OESMSG_QRYMSG_CRD_DRAWABLE_BALANCE      = 0x90  # 0x90/138 查询融资融券业务可取资金
    OESMSG_QRYMSG_CRD_COLLATERAL_TRANSFER_OUT_MAX_QTY \
                                            = 0x91  # 0x91/139 查询融资融券担保品可转出的最大数量

    # 公共的会话类消息
    OESMSG_SESS_HEARTBEAT                   = 0xFA  # 0xFA/250 心跳消息
    OESMSG_SESS_TEST_REQUEST                = 0xFB  # 0xFB/251 测试请求消息
    OESMSG_SESS_LOGIN_EXTEND                = 0xFC  # 0xFC/252 登录扩展消息
    OESMSG_SESS_LOGOUT                      = 0xFE  # 0xFE/254 登出消息
# -------------------------


class OesChangePasswordReqT(Structure):
    """修改密码请求报文"""
    _fields_ = [
        ("encryptMethod", c_int32),             # 加密方法
        ("__filler", c_int32),                  # 按64位对齐的填充域
        # 登录用户名
        ("username", c_char * OES_CLIENT_NAME_MAX_LEN),
        # 用户私有信息 (由客户端自定义填充, 并在回报数据中原样返回)
        ('userInfo', UnionForUserInfo),
        # 之前的登录密码
        ("oldPassword", c_char * OES_PWD_MAX_LEN),
        # 新的登录密码
        ("newPassword", c_char * OES_PWD_MAX_LEN),
    ]


class OesChangePasswordRspT(Structure):
    """修改密码结构体定义"""
    _fields_ = (
        ("encryptMethod", c_int32),             # 加密方法
        ("__filler", c_int32),                  # 按64位对齐的填充域
        # 登录用户名
        ("username", c_char * OES_CLIENT_NAME_MAX_LEN),
        # 用户私有信息 (由客户端自定义填充, 并在应答数据中原样返回)
        ("userInfo", UnionForUserInfo),
        ("clientId", c_int16),                  # 客户端编号
        ("clEnvId", c_int8),                    # 客户端环境号
        ("__filler2", c_int8),                  # 按64位对齐的填充域
        ("transDate", c_int32),                 # 发生日期 (格式为 YYYYMMDD, 形如 20160830)
        ("transTime", c_int32),                 # 发生时间 (格式为 HHMMSSsss, 形如 141205000)
        ("rejReason", c_int32),                 # 拒绝原因
    )


class OesNotifyInfoReportT(Structure):
    """
    通知消息的结构体定义

    __OES_NOTIFY_BASE_INFO_PKT
    """
    _fields_ = [
        ("notifySeqNo", c_int32),               # 通知消息序号
        ("notifySource", c_uint8),              # 通知消息来源 @see eOesNotifySourceT
        ("notifyType", c_uint8),                # 通知消息类型 @see eOesNotifyTypeT
        ("notifyLevel", c_uint8),               # 通知消息等级 @see eOesNotifyLevelT
        ("notifyScope", c_uint8),               # 通知范围 @see eOesNotifyScopeT
        ("tranTime", c_int32),                  # 通知发出时间 (格式为 HHMMSSsss, 形如 141205000)
        ("businessType", c_uint8),              # 业务类型 @see eOesBusinessTypeT
        ("__NOTIFY_INFO_filler1", c_uint8 * 3), # 按64位对齐的填充域
        # 客户代码 (仅当消息通知范围为指定客户时有效)
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        # 证券代码 (仅当通知消息与特定证券相关时有效)
        ("securityId", c_char * OES_SECURITY_ID_MAX_LEN),
        ("mktId", c_uint8),                     # 市场代码 (仅用于修饰证券代码) @see eOesMarketIdT
        ("__NOTIFY_INFO_filler2", c_uint8 * 3), # 按64位对齐的填充域
        ("contentLen", c_int32),                # 通知内容长度 (不包含'\0'结束符的有效字符长度)
        # 通知内容
        ("content", c_char * OES_NOTIFY_CONTENT_MAX_LEN),
    ]


class OesTestRequestRspT(Structure):
    """
    测试请求回报的结构体定义

    _OesTestRequestRspT
    __OES_TEST_REQ_LATENCY_FIELDS
    """
    _fields_ = (
        # 测试请求标识符
        ("testReqId", c_char * OES_MAX_TEST_REQ_ID_LEN),
        # 测试请求的原始发送时间 (timeval结构或形如'YYYYMMDD-HH:mm:SS.sss'的字符串)
        ("origSendTime", c_char * OES_MAX_SENDING_TIME_LEN),
        # 按64位对齐的填充域
        ("__filler1", c_char * 2),
        # 测试请求应答的发送时间 (timeval结构或形如'YYYYMMDD-HH:mm:SS.sss'的字符串)
        ("respTime", c_char * OES_MAX_SENDING_TIME_LEN),
        # 按64位对齐的填充域
        ("__filler2", c_char * 2),
        # 消息实际接收时间 (开始解码等处理之前的时间)
        ("recvTime", STimespec32T),
        # 消息采集处理完成时间
        ("collectedTime", STimespec32T),
        # 消息推送时间 (写入推送缓存以后, 实际网络发送之前)
        ("pushingTime", STimespec32T),
    )


class OesOptSettlementConfirmReqT(Structure):
    """
    期权账户结算单确认请求报文
    """
    _fields_ = [
        # 客户代码
        ('custId', c_char * OES_CUST_ID_MAX_LEN),
        # 用户私有信息 (由客户端自定义填充, 并在回报数据中原样返回)
        ("userInfo", UnionForUserInfo),
    ]


class OesReportSynchronizationRspT(Structure):
    """
    回报同步应答消息
    """
    _fields_ = (
        # 服务端最后已发送或已忽略的回报数据的回报编号
        ("lastRptSeqNum", c_int64),
        # 待订阅的客户端环境号
        # - 大于0, 区分环境号, 仅订阅环境号对应的回报数据
        # - 小于等于0, 不区分环境号, 订阅该客户下的所有回报数据
        ("subscribeEnvId", c_int8),
        # 按64位对齐的填充域
        ("__filler", c_uint8 * 3),
        # 已订阅的回报消息种类
        ("subscribeRptTypes", c_int32),
    )


class OesApiSubscribeInfoT(Structure):
    """
    回报订阅的订阅参数信息
    """
    _fields_ = [
        # 待订阅的客户端环境号
        # - 大于0, 区分环境号, 仅订阅环境号对应的回报数据
        # - 小于等于0, 不区分环境号, 订阅该客户下的所有回报数据
        ("clEnvId", c_int8),
        # 按64位对齐的填充域
        ("__filler", c_uint8 * 3),
        # 待订阅的回报消息种类
        # - 0:      默认回报 (等价于: 0x01,0x02,0x04,0x08,0x10,0x20,0x40, 0x80,0x200,0x400,0x800,0x1000)
        # - 0x0001: OES业务拒绝 (未通过风控检查等)
        # - 0x0002: OES委托已生成 (已通过风控检查)
        # - 0x0004: 交易所委托回报 (包括交易所委托拒绝、委托确认和撤单完成通知)
        # - 0x0008: 交易所成交回报
        # - 0x0010: 出入金委托执行报告 (包括出入金委托拒绝、出入金委托回报)
        # - 0x0020: 资金变动信息
        # - 0x0040: 持仓变动信息
        # - 0x0080: 市场状态信息
        # - 0x0100: 通知消息回报
        # - 0x0200: 结算单确认消息 (仅期权业务)
        # - 0x0400: 融资融券直接还款委托执行报告 (仅信用业务)
        # - 0x0800: 融资融券合约变动信息 (仅信用业务)
        # - 0x1000: 融资融券合约流水信息 (仅信用业务)
        # - 0xFFFF: 所有回报
        # @see eOesSubscribeReportTypeT
        ("rptTypes", c_int32)
    ]


class OesRptMsgHeadT(Structure):
    """
    回报消息的消息头定义
    """
    _fields_ = (
        ('rptSeqNum', c_int64),                 # 回报消息的编号
        ('rptMsgType', c_uint8),                # 回报消息的消息代码 @see eOesMsgTypeT
        ('execType', c_uint8),                  # 执行类型 @see eOesExecTypeT
        ('bodyLength', c_int16),                # 回报消息的消息体大小
        ('ordRejReason', c_int32),              # 订单/撤单被拒绝原因
    )


class OesRptMsgBodyT(Union):
    """
    回报消息的消息体定义
    """
    _fields_ = [
        # OES委托响应-委托已生成
        ("ordInsertRsp", OesOrdCnfmT),
        # OES委托响应-业务拒绝
        ("ordRejectRsp", OesOrdRejectT),
        # 交易所委托回报
        ("ordCnfm", OesOrdCnfmT),
        # 交易所成交回报
        ("trdCnfm", OesTrdCnfmT),
        # 出入金委托拒绝
        ("fundTrsfRejectRsp", OesFundTrsfRejectT),
        # 出入金执行报告
        ("fundTrsfCnfm", OesFundTrsfReportT),
        # 资金变动回报信息
        ("cashAssetRpt", OesCashAssetReportT),
        # 持仓变动回报信息 (股票)
        ("stkHoldingRpt", OesStkHoldingReportT),
        # 持仓变动回报信息 (期权)
        ("optHoldingRpt", OesOptHoldingReportT),
        # 期权标的持仓变动回报信息
        ("optUnderlyingHoldingRpt", OesOptUnderlyingHoldingReportT),
        # 通知消息回报信息
        ("notifyInfoRpt", OesNotifyInfoReportT),
        # 期权账户结算单确认回报信息
        ("optSettlementConfirmRpt", OesOptSettlementConfirmReportT),
        # 融资融券直接还款执行报告
        ("crdDebtCashRepayRpt", OesCrdCashRepayReportT),
        # 融资融券合约变动回报信息
        ("crdDebtContractRpt", OesCrdDebtContractReportT),
        # 融资融券合约流水回报信息
        ("crdDebtJournalRpt", OesCrdDebtJournalReportT),
    ]


class OesRptMsgT(Structure):
    """
    完整的回报消息定义
    """
    _fields_ = (
        ("rptHead", OesRptMsgHeadT),    # 回报消息的消息头
        ("rptBody", OesRptMsgBodyT)     # 回报消息的消息体
    )


class OesRspMsgBodyT(Union):
    """
    汇总的应答消息的消息体定义
    """
    _fields_ = [
        # 执行报告回报消息
        ("rptMsg", OesRptMsgT),
        # 市场状态消息
        ("mktStateRpt", OesMarketStateInfoT),
        # 测试请求的应答报文
        ("testRequestRsp", OesTestRequestRspT),
        # 回报同步应答报文
        ("reportSynchronizationRsp", OesReportSynchronizationRspT),
        # 修改密码应答报文
        ("changePasswordRsp", OesChangePasswordRspT),
        # 结算单确认应答报文
        ("optSettlementConfirmRsp", OesOptSettlementConfirmRspT),
    ]
