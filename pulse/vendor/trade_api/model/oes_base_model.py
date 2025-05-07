# -*- coding: utf-8 -*-
"""现货基本领域模型相关结构体"""

from functools import reduce
from ctypes import (
    c_char, c_uint8, c_int8, c_int16, c_uint32, c_int32, c_int64,
    Structure, Union
)

try:
    from .spk_util import (
        SPK_MAX_PATH_LEN, STimespec32T, UnionForUserInfo
    )
except ImportError:
    from sutil.spk_util import (
        SPK_MAX_PATH_LEN, STimespec32T, UnionForUserInfo
    )

from .oes_base_constants import (
    OES_SECURITY_NAME_MAX_LEN, OES_INV_ACCT_ID_MAX_LEN,
    OES_SECURITY_ID_MAX_LEN, OES_EXCH_ORDER_ID_MAX_LEN,
    OES_CASH_ACCT_ID_MAX_LEN, OES_CUST_ID_MAX_LEN,
    OES_MAX_ERROR_INFO_LEN, OES_MAX_ALLOT_SERIALNO_LEN,
    OES_PWD_MAX_LEN, OES_CREDIT_DEBT_ID_MAX_LEN
)
from .oes_base_model_credit import (
    OesCrdSecurityDebtStatsBaseInfoT, OesCrdCreditAssetBaseInfoT, _CreditExtT
)
from .oes_base_model_option import _OesOptionAssetExtInfoT


# ===================================================================
# 委托信息的结构体定义
# ===================================================================

# 委托信息的基础内容定义
__OES_ORD_BASE_INFO_PKT = [
    # 客户委托流水号 (必填. 由客户端维护的递增流水, 用于识别重复的委托申报)
    ("clSeqNo", c_int32),
    # 市场代码 (必填) @see eOesMarketIdT
    ("mktId", c_uint8),
    # 订单类型 (必填) @see eOesOrdTypeShT eOesOrdTypeSzT
    ("ordType", c_uint8),
    # 买卖类型 (必填) @see eOesBuySellTypeT
    ("bsType", c_uint8),
    # 指定关联的交易网关 (0:不指定网关, 大于0:指定网关条目编号)
    ("assignedTgwItemNo", c_uint8),
    # 证券账户 (选填, 若为空则自动填充)
    ("invAcctId", c_char * OES_INV_ACCT_ID_MAX_LEN),
    # 证券代码 (必填, 例外: 撤单委托和组合行权委托的证券代码可不填)
    ("securityId", c_char * OES_SECURITY_ID_MAX_LEN),
    # 委托数量 (单位: 股/张/份)
    ("ordQty", c_int32),
    # 委托价格, 单位精确到元后四位, 即1元 = 10000
    ("ordPrice", c_int32),
    # 原始订单(待撤销的订单)的客户订单编号 (仅撤单时需要填充)
    ("origClOrdId", c_int64),
    # 用户私有信息 (由客户端自定义填充, 并在回报数据中原样返回)
    ("userInfo", UnionForUserInfo),
]


# 撤单请求的基础内容定义
__OES_ORD_CANCEL_BASE_INFO_PKT = [
    # 客户委托流水号 (由客户端维护的递增流水, 用于识别重复的委托申报, 必填)
    ("clSeqNo", c_int32),
    # 市场代码 (必填) @see eOesMarketIdT
    ("mktId", c_uint8),
    # 按64位对齐的填充域
    ("__ORD_CANCEL_BASE_INFO_filler1", c_uint8),
    # 按64位对齐的填充域
    ("__ORD_CANCEL_BASE_INFO_filler2", c_uint8),
    # 指定关联的交易网关 (0:不指定网关, 大于0:指定网关条目编号)
    ("assignedTgwItemNo", c_uint8),
    # 证券账户 (选填, 若不为空则校验待撤订单是否匹配)
    ("invAcctId", c_char * OES_INV_ACCT_ID_MAX_LEN),
    # 证券代码 (选填, 若不为空则校验待撤订单是否匹配)
    ("securityId", c_char * OES_SECURITY_ID_MAX_LEN),
    # 原始订单(待撤销的订单)的客户委托流水号 (若使用 origClOrdId, 则不必填充该字段)
    ("origClSeqNo", c_int32),
    # 原始订单(待撤销的订单)的客户端环境号 (小于等于0, 则使用当前会话的 clEnvId)
    ("origClEnvId", c_int8),
    # 按64位对齐的填充域
    ("__ORD_CANCEL_BASE_INFO_filler3", c_uint8 * 3),
    # 原始订单(待撤销的订单)的客户订单编号 (若使用 origClSeqNo, 则不必填充该字段)
    ("origClOrdId", c_int64),
    # 用户私有信息 (由客户端自定义填充, 并在回报数据中原样返回)
    ("userInfo", UnionForUserInfo),
]


# 委托请求中的时间戳字段定义 (用于记录打点信息以统计延迟)
__OES_ORD_REQ_LATENCY_FIELDS = [
    # 委托请求的客户端原始发送时间 (OES内部使用, 由API在发送时自动填充)
    ("ordReqOrigSendTime", STimespec32T)
]


# 委托回报中的时间戳字段定义 (用于记录打点信息以统计延迟) */
__OES_ORD_CNFM_LATENCY_FIELDS = [
    ("ordReqOrigRecvTime", STimespec32T),       # 委托请求的初始接收时间
    ("ordReqCollectedTime", STimespec32T),      # 委托请求的入队时间
    ("ordReqActualDealTime", STimespec32T),     # 委托请求的实际处理开始时间
    ("ordReqProcessedTime", STimespec32T),      # 委托请求的处理完成时间
    ("ordCnfmOrigRecvTime", STimespec32T),      # 委托确认的开始采集时间
    ("ordCnfmCollectedTime", STimespec32T),     # 委托确认的采集完成时间
    ("ordCnfmActualDealTime", STimespec32T),    # 委托确认的实际处理开始时间
    ("ordCnfmProcessedTime", STimespec32T),     # 委托确认的处理完成时间
    ("ordDeclareTime", STimespec32T),           # 初始报盘时间
    ("ordDeclareDoneTime", STimespec32T),       # 报盘完成时间
    ("pushingTime", STimespec32T),              # 消息推送时间 (写入推送缓存以后, 实际网络发送之前)
]


# 用于控制委托请求中的时间戳字段是否定义 (用于记录打点信息以统计延迟) 需与api宏定义相同的值
# 默认开启用于统计延时的打点信息
_OES_EXPORT_LATENCY_STATS = True


# 委托确认基础信息的内容定义
__OES_ORD_CNFM_BASE_INFO_PKT = [
    ("clOrdId", c_int64),                       # 客户订单编号 (在OES内具有唯一性的内部委托编号)
    ("clientId", c_int16),                      # 客户端编号
    ("clEnvId", c_int8),                        # 客户端环境号
    ("origClEnvId", c_int8),                    # 原始订单(待撤销的订单)的客户端环境号 (仅适用于撤单委托)
    ("origClSeqNo", c_int32),                   # 原始订单(待撤销的订单)的客户委托流水号 (仅适用于撤单委托)
    ("ordDate", c_int32),                       # 委托日期 (格式为 YYYYMMDD, 形如 20160830)
    ("ordTime", c_int32),                       # 委托时间 (格式为 HHMMSSsss, 形如 141205000)
    ("ordCnfmTime", c_int32),                   # 委托确认时间 (格式为 HHMMSSsss, 形如 141206000)
    ("ordStatus", c_uint8),                     # 订单当前状态 @see eOesOrdStatusT
    ("ordCnfmSts", c_uint8),                    # 委托确认状态 (交易所返回的回报状态, 仅供参考)  @see eOesOrdStatusT
    ("securityType", c_uint8),                  # 证券类型 @see eOesSecurityTypeT
    ("subSecurityType", c_uint8),               # 证券子类型 @see eOesSubSecurityTypeT
    ("_platformId", c_uint8),                   # 平台号 (OES内部使用) @see eOesPlatformIdT
    ("_tgwGrpNo", c_uint8),                     # 交易网关组序号 (OES内部使用)
    ("_tgwItemNo", c_uint8),                    # 交易网关条目编号
    ("productType", c_uint8),                   # 产品类型 @see eOesProductTypeT
    ("exchOrdId", c_char * OES_EXCH_ORDER_ID_MAX_LEN),
                                                # 交易所订单编号 (深交所的订单编号是16位的非数字字符串)
    ("_declareFlag", c_uint8),                  # 已报盘标志 (OES内部使用)
    ("_repeatFlag", c_uint8),                   # 重复回报标志 (OES内部使用)
    ("ownerType", c_uint8),                     # 所有者类型 @see eOesOwnerTypeT
    ("frzAmt", c_int64),                        # 委托当前冻结的交易金额
    ("frzInterest", c_int64),                   # 委托当前冻结的利息
    ("frzFee", c_int64),                        # 委托当前冻结的交易费用
    ("cumAmt", c_int64),                        # 委托累计已发生的交易金额
    ("cumInterest", c_int64),                   # 委托累计已发生的利息
    ("cumFee", c_int64),                        # 委托累计已发生的交易费用
    ("cumQty", c_int32),                        # 累计执行数量 (累计成交数量)
    ("canceledQty", c_int32),                   # 已撤单数量
    ("ordRejReason", c_int32),                  # 订单/撤单拒绝原因
    ("exchErrCode", c_int32),                   # 交易所错误码
    ("pbuId", c_int32),                         # PBU代码 (席位号)
    ("branchId", c_int32),                      # 交易营业部代码
    ("_rowNum", c_int32),                       # 回报记录号 (OES内部使用)
    ("_recNum", c_uint32),                      # OIW委托编号 (OES内部使用)
]


# 委托确认扩展信息的内容定义
__OES_ORD_CNFM_EXT_INFO_PKT = [
    ("frzMargin", c_int64),                     # 委托当前冻结的保证金
    ("cumMargin", c_int64),                     # 委托累计已使用的保证金
    ("businessType", c_uint8),                  # 业务类型 @see eOesBusinessTypeT
    ("mandatoryFlag", c_uint8),                 # 强制标志 @see eOesOrdMandatoryFlagT
    ("repayMode", c_uint8),                     # 归还模式 (仅适用于卖券还款委托) @see eOesCrdDebtRepayModeT
    ("__ORD_CNFM_EXT_filler", c_uint8 * 5),     # 按64位对齐的填充域
    ("__ORD_CNFM_EXT_reserve", c_char * 16),    # 预留的备用字段
]


class OesOrdReqT(Structure):
    """
    委托请求的结构体定义

    __OES_ORD_BASE_INFO_PKT
    __OES_ORD_REQ_LATENCY_FIELDS
    """


class OesOrdCancelReqT(Structure):
    """
    撤单请求的结构体定义

    __OES_ORD_CANCEL_BASE_INFO_PKT
    __OES_ORD_REQ_LATENCY_FIELDS
    """


# 委托拒绝(OES业务拒绝)的结构体定义
__OES_ORD_REJECT_EXT_PKT = [
    ("origClSeqNo", c_int32),                   # 原始订单(待撤销的订单)的客户委托流水号 (仅适用于撤单请求)
    ("origClEnvId", c_int8),                    # 原始订单(待撤销的订单)的客户端环境号 (仅适用于撤单请求)
    ("clEnvId", c_int8),                        # 客户端环境号
    ("clientId", c_int16),                      # 客户端编号
    ("ordDate", c_int32),                       # 委托日期 (格式为 YYYYMMDD, 形如 20160830)
    ("ordTime", c_int32),                       # 委托时间 (格式为 HHMMSSsss, 形如 141205000)
    ("ordRejReason", c_int32),                  # 订单拒绝原因
    ("businessType", c_uint8),                  # 业务类型 @see eOesBusinessTypeT
    ("__filler", c_uint8 * 3),                  # 按64位对齐的填充域
]


class OesOrdRejectT(Structure):
    """
    委托拒绝(OES业务拒绝)的结构体定义

    __OES_ORD_BASE_INFO_PKT
    __OES_ORD_REQ_LATENCY_FIELDS
    __OES_ORD_REJECT_EXT_PKT
    """


class OesOrdCnfmT(Structure):
    """
    委托确认的结构体定义

    __OES_ORD_BASE_INFO_PKT
    __OES_ORD_REQ_LATENCY_FIELDS
    __OES_ORD_CNFM_BASE_INFO_PKT
    __OES_ORD_CNFM_EXT_INFO_PKT
    """
# -------------------------


# ===================================================================
# 融资融券负债归还请求的结构体定义
# ===================================================================

# OesCrdRepayReqT = OesOrdReqT + repayMode + debtId
# 请参见 @see oes_api.send_credit_repay_req 具体实现
# -------------------------


# ===================================================================
# 融资融券直接还款请求的结构体定义
# ===================================================================

# 融资融券直接还款请求的基础内容定义
__OES_CRD_CASH_REPAY_REQ_BASE_PKT = [
    ("clSeqNo", c_int32),                       # 客户委托流水号 (由客户端维护的递增流水)
    ("repayMode", c_uint8),                     # 归还模式 @see eOesCrdAssignableRepayModeT
    ("repayJournalType", c_uint8),              # 归还指令类型 @see eOesCrdDebtJournalTypeT
    ("__CRD_CASH_REPAY_REQ_BASE_filler", c_uint8 * 2),
                                                # 按64位对齐的填充域
    ("repayAmt", c_int64),                      # 归还金额 (单位精确到元后四位, 即1元=10000. @note 实际还款金额会向下取整到分)

    # 资金账户代码
    ("cashAcctId", c_char * OES_CASH_ACCT_ID_MAX_LEN),
    # 指定归还的合约编号
    ("debtId", c_char * OES_CREDIT_DEBT_ID_MAX_LEN),
    # 用户私有信息 (由客户端自定义填充, 并在回报数据中原样返回)
    ("userInfo", UnionForUserInfo)
]


# OesCrdCashRepayReqT 暂未使用, 无需定义


__OES_CRD_CASH_REPAY_REPORT_EXT_PKT = [
    # 证券账户 (仅适用于管理端现金了结/场外了结融券负债委托回报)
    ("invAcctId", c_char * OES_INV_ACCT_ID_MAX_LEN),
    # 证券代码 (仅适用于管理端现金了结/场外了结融券负债委托回报)
    ("securityId", c_char * OES_SECURITY_ID_MAX_LEN),
    ("mktId", c_uint8),                         # 市场代码 @see eOesMarketIdT
    ("__filler1", c_uint8 * 7),                 # 按64位对齐的填充域
    ("ordPrice", c_int32),                      # 委托价格 (公允价格, 仅适用于管理端现金了结/场外了结融券负债委托回报; 单位精确到元后四位, 即1元=10000)
    ("ordQty", c_int32),                        # 归还数量 (仅适用于管理端现金了结/场外了结融券负债委托回报)
    ("ordDate", c_int32),                       # 委托日期 (格式为 YYYYMMDD, 形如 20160830)
    ("ordTime", c_int32),                       # 委托时间 (格式为 HHMMSSsss, 形如 141205000)
    ("clOrdId", c_int64),                       # 客户订单编号 (在OES内具有唯一性的内部委托编号, 只有有效的委托才会生成, 被拒绝的委托该字段为0)
    ("clientId", c_int16),                      # 客户端编号
    ("clEnvId", c_int8),                        # 客户端环境号
    ("mandatoryFlag", c_uint8),                 # 委托强制标志
    ("ordStatus", c_uint8),                     # 订单当前状态 @see eOesOrdStatusT
    ("ownerType", c_uint8),                     # 所有者类型 (被拒绝的委托该字段为0) @see eOesOwnerTypeT
    ("__filler2", c_uint8 * 2),                 # 按64位对齐的填充域
    ("ordRejReason", c_int32),                  # 订单拒绝原因
    ("repaidQty", c_int32),                     # 实际归还数量 (仅适用于管理端现金了结/场外了结融券负债委托回报)
    ("repaidAmt", c_int64),                     # 实际归还金额 (单位精确到元后四位, 即1元=10000)
    ("repaidFee", c_int64),                     # 实际归还费用 (单位精确到元后四位, 即1元=10000)
    ("repaidInterest", c_int64),                # 实际归还利息 (单位精确到元后四位, 即1元=10000)
    ("branchId", c_int32),                      # 交易营业部编号 (被拒绝的委托该字段为0)
    ("__filler3", c_int32),                     # 按64位对齐的填充域
]


class OesCrdCashRepayReportT(Structure):
    """
    融资融券直接还款请求执行状态回报的结构体定义

    __OES_CRD_CASH_REPAY_REQ_BASE_PKT
    __OES_ORD_REQ_LATENCY_FIELDS
    __OES_CRD_CASH_REPAY_REPORT_EXT_PKT
    """
# -------------------------


# ===================================================================
# 成交回报信息的结构体定义
# ===================================================================

# 成交基础信息的内容定义
__OES_TRD_BASE_INFO_PKT = [
    ("exchTrdNum", c_int64),                    # 交易所成交编号 (以下的6个字段是成交信息的联合索引字段)
    ("mktId", c_uint8),                         # 市场代码 @see eOesMarketIdT
    ("trdSide", c_uint8),                       # 买卖类型 (取值范围: 买/卖, 申购/赎回) @see eOesBuySellTypeT
    ("_platformId", c_uint8),                   # 平台号 (OES内部使用) @see eOesPlatformIdT
    ("_trdCnfmType", c_uint8),                  # 成交类型 (OES内部使用) @see eOesTrdCnfmTypeT
    ("_etfTrdCnfmSeq", c_uint32),               # ETF成交回报顺序号 (OES内部使用), 为区分ETF成交记录而设置 (以订单为单位)

    # 股东账户代码
    ("invAcctId", c_char * OES_INV_ACCT_ID_MAX_LEN),
    # 证券代码
    ("securityId", c_char * OES_SECURITY_ID_MAX_LEN),

    ("trdDate", c_int32),                       # 成交日期 (格式为 YYYYMMDD, 形如 20160830)
    ("trdTime", c_int32),                       # 成交时间 (格式为 HHMMSSsss, 形如 141205000)
    ("trdQty", c_int32),                        # 成交数量
    ("trdPrice", c_int32),                      # 成交价格 (单位精确到元后四位, 即: 1元=10000)
    ("trdAmt", c_int64),                        # 成交金额 (单位精确到元后四位, 即: 1元=10000)
    ("clOrdId", c_int64),                       # 客户订单编号
    ("cumQty", c_int32),                        # 累计执行数量
    ("_rowNum", c_int32),                       # 回报记录号 (OES内部使用)
    ("_tgwGrpNo", c_uint8),                     # 交易网关组序号 (OES内部使用)
    ("_etfCashType", c_uint8),                  # ETF资金记录类型, 仅当成交类型为ETF资金记录时此字段有效 @see eOesEtfCashTypeT
    ("_tgwItemNo", c_uint8),                    # 交易网关条目编号
    ("productType", c_uint8),                   # 产品类型 @see eOesProductTypeT
    ("origOrdQty", c_int32),                    # 原始委托数量
    ("pbuId", c_int32),                         # PBU代码 (席位号)
    ("branchId", c_int32),                      # 交易营业部代码
]


# 成交回报中的时间戳字段定义 (用于记录打点信息以统计延迟)
__OES_TRD_CNFM_LATENCY_FIELDS = [
    ("trdCnfmOrigRecvTime", STimespec32T),     # 成交确认的开始采集时间
    ("trdCnfmCollectedTime", STimespec32T),    # 成交确认的采集完成时间
    ("trdCnfmActualDealTime", STimespec32T),   # 成交确认的实际处理开始时间 (POC测试时会被复用于存储委托请求的原始发送时间)
    ("trdCnfmProcessedTime", STimespec32T),    # 成交确认的处理完成时间
    ("pushingTime", STimespec32T)              # 消息推送时间 (写入推送缓存以后, 实际网络发送之前)
]


# 成交回报信息的内容定义
__OES_TRD_CNFM_BASE_INFO_PKT = [
    ("clSeqNo", c_int32),                       # 客户委托流水号
    ("clientId", c_int16),                      # 客户端编号
    ("clEnvId", c_int8),                        # 客户端环境号
    ("subSecurityType", c_uint8),               # 证券子类别 (为保持兼容而位置凌乱, 后续会做调整) @see eOesSubSecurityTypeT
    ("ordStatus", c_uint8),                     # 订单当前状态 @see eOesOrdStatusT
    ("ordType", c_uint8),                       # 订单类型 @see eOesOrdTypeShT eOesOrdTypeSzT
    ("ordBuySellType", c_uint8),                # 买卖类型 @see eOesBuySellTypeT
    ("securityType", c_uint8),                  # 证券类型 @see eOesSecurityTypeT
    ("origOrdPrice", c_int32),                  # 原始委托价格, 单位精确到元后四位, 即1元 = 10000
    ("cumAmt", c_int64),                        # 累计成交金额
    ("cumInterest", c_int64),                   # 累计成交利息
    ("cumFee", c_int64),                        # 累计交易费用
    ("userInfo", UnionForUserInfo),             # 用户私有信息 (由客户端自定义填充, 并在回报数据中原样返回)
]


# 成交回报信息的内容定义
__OES_TRD_CNFM_EXT_INFO_PKT = [
    ("trdInterest", c_int64),                   # 债券利息
    ("trdFee", c_int64),                        # 交易费用
    ("trdMargin", c_int64),                     # 占用/释放的保证金
    ("cumMargin", c_int64),                     # 累计占用/释放的保证金
    ("businessType", c_uint8),                  # 业务类型 @see eOesBusinessTypeT
    ("mandatoryFlag", c_uint8),                 # 强制标志 @see eOesOrdMandatoryFlagT
    ("ownerType", c_uint8),                     # 所有者类型 @see eOesOwnerTypeT
    ("__TRD_CNFM_EXT_filler", c_uint8 * 5),     # 按64位对齐的填充域
    ("__TRD_CNFM_EXT_reserve", c_char * 16),    # 预留的备用字段
]


# OesTrdBaseInfoT 暂未使用, 无需定义


class OesTrdCnfmT(Structure):
    """
    成交回报结构体定义

    __OES_TRD_BASE_INFO_PKT
    __OES_TRD_CNFM_BASE_INFO_PKT
    __OES_TRD_CNFM_LATENCY_FIELDS
    __OES_TRD_CNFM_EXT_INFO_PKT
    """
# -------------------------


# ===================================================================
# 新股配号、中签记录信息 (OesLotWinningBaseInfo) 定义
# ===================================================================

# 新股配号、中签记录信息的内容定义
__OES_LOT_WINNING_BASE_INFO_PKT = [
    # 证券账户
    ("invAcctId", c_char * OES_INV_ACCT_ID_MAX_LEN),
    # 配号代码/中签代码
    ("securityId", c_char * OES_SECURITY_ID_MAX_LEN),
    # 市场代码 @see eOesMarketIdT
    ("mktId", c_uint8),
    # 记录类型 @see eOesLotTypeT
    ("lotType", c_uint8),

    ("rejReason", c_uint8),                     # 失败原因, 当且仅当 lotType 为 OES_LOT_TYPE_FAILED 时此字段有效 @see eOesLotRejReasonT
    ("__LOT_WINNING_BASE_INFO_filler", c_int8), # 按64位对齐的填充域
    ("lotDate", c_int32),                       # 配号日期/中签日期 (格式为 YYYYMMDD, 形如 20160830)
    # 证券名称 (UTF-8 编码)
    ("securityName", c_char * OES_SECURITY_NAME_MAX_LEN),
    ("assignNum", c_int64),                     # 起始配号号码 (当为中签记录时此字段固定为0)
    ("lotQty", c_int32),                        # 配号成功数量/中签股数
    ("lotPrice", c_int32),                      # 最终发行价, 单位精确到元后四位, 即1元 = 10000。当为配号记录时此字段值固定为0
    ("lotAmt", c_int64),                        # 中签金额, 单位精确到元后四位, 即1元 = 10000。当为配号记录时此字段值固定为0
]


class OesLotWinningBaseInfoT(Structure):
    """
    新股配号、中签记录信息定义

    __OES_LOT_WINNING_BASE_INFO_PKT
    """
# -------------------------


# ===================================================================
# 出入金信息的结构体定义
# ===================================================================

# 出入金委托基础信息的内容定义
__OES_FUND_TRSF_BASE_INFO_PKT = [
    ("clSeqNo", c_int32),                       # 客户委托流水号 (由客户端维护的递增流水)
    ("direct", c_uint8),                        # 划转方向 @see eOesFundTrsfDirectT
    ("fundTrsfType", c_uint8),                  # 出入金转账类型 @see eOesFundTrsfTypeT
    ("__FUND_TRSF_BASE_filler", c_uint8 * 2),   # 按64位对齐的填充域

    # 资金账户代码 (可以为空, 为空则自动填充)
    ("cashAcctId", c_char * OES_CASH_ACCT_ID_MAX_LEN),

    # 交易密码 (沪深OES之间内部资金划拨时无需填写该字段, 其它场景该字段必填)
    ("trdPasswd", c_char * OES_PWD_MAX_LEN),

    # 转账密码
    # 转账方向为转入(银行转证券)时, 此密码为银行密码,
    # 转账方向为转出(证券转银行)时, 此密码为主柜资金密码
    # OES和主柜之间划拨资金时, 此密码为主柜资金密码
    # 沪深OES之间内部资金划拨时, 无需填写该字段
    ("trsfPasswd", c_char * OES_PWD_MAX_LEN),

    # 发生金额 (单位精确到元后四位, 即1元=10000), 无论入金还是出金,
    # 发生金额的取值都应为正数, 精度将被自动向下舍入到分,
    # 例如: 金额 1.9999 将被自动转换为 1.9900
    ("occurAmt", c_int64),

    ("userInfo", UnionForUserInfo),             # int64 类型的用户私有信息
]


class OesFundTrsfReqT(Structure):
    """
    出入金请求定义

    __OES_FUND_TRSF_BASE_INFO_PKT
    """
    _hiden_attributes = ["trsfPasswd", "trdPasswd"]


# 出入金拒绝的回报扩展结构定义
__OES_FUND_TRSF_EXT_PKT = [
    ("ordDate", c_int32),                       # 委托日期 (格式为 YYYYMMDD, 形如 20160830)
    ("ordTime", c_int32),                       # 委托时间 (格式为 HHMMSSsss, 形如 141205000)
    ("clientId", c_int16),                      # 客户端编号
    ("clEnvId", c_int8),                        # 客户端环境号
    ("__filler", c_int8),                       # 64位对齐的填充域
    ("rejReason", c_int32),                     # 错误码
    ("errorInfo", c_char * OES_MAX_ERROR_INFO_LEN)
                                                # 错误信息
]


class OesFundTrsfRejectT(Structure):
    """
    出入金拒绝的回报结构定义 (因风控检查未通过而被OES拒绝)

    __OES_FUND_TRSF_BASE_INFO_PKT
    __OES_FUND_TRSF_EXT_PKT
    """
    _hiden_attributes = ["trsfPasswd", "trdPasswd"]


class OesFundTrsfReportT(Structure):
    """
    出入金委托执行状态回报的结构体定义
    """
    _fields_ = [
        ("clSeqNo", c_int32),                   # 客户委托流水号 (由客户端维护的递增流水)
        ("clientId", c_int16),                  # 客户端编号
        ("clEnvId", c_int8),                    # 客户端环境号
        ("direct", c_uint8),                    # 划转方向 @see eOesFundTrsfDirectT
        # 资金账户代码
        ("cashAcctId", c_char * OES_CASH_ACCT_ID_MAX_LEN),

        # 发生金额 (单位精确到元后四位, 即1元=10000), 无论入金还是出金,
        # 发生金额的取值都应为正数, 精度将被自动向下舍入到分,
        # 例如: 金额 1.9999 将被自动转换为 1.9900
        ("occurAmt", c_int64),
        # 用户私有信息 (由客户端自定义填充, 并在回报数据中原样返回)
        ("userInfo", UnionForUserInfo),

        ("fundTrsfId", c_int32),                # OES出入金委托编号 (在OES内具有唯一性的内部出入金委托编号)
        ("counterEntrustNo", c_int32),          # 柜台出入金委托编号
        ("operDate", c_int32),                  # 出入金委托日期 (格式为 YYYYMMDD, 形如 20160830)
        ("operTime", c_int32),                  # 出入金委托时间 (格式为 HHMMSSsss, 形如 141205000)
        ("dclrTime", c_int32),                  # 上报柜台时间 (格式为 HHMMSSsss, 形如 141205000)
        ("doneTime", c_int32),                  # 柜台执行结果采集时间 (格式为 HHMMSSsss, 形如 141205000)
        ("fundTrsfType", c_uint8),              # 出入金转账类型 @see eOesFundTrsfTypeT
        ("trsfStatus", c_uint8),                # 出入金委托执行状态 @see eOesFundTrsfStatusT
        ("_hasCounterTransfered", c_uint8),     # 是否有转账到主柜
        ("fundTrsfSourceType", c_uint8),        # 指令来源 @see eOesFundTrsfSourceTypeT
        ("rejReason", c_int32),                 # 错误原因
        ("counterErrCode", c_int32),            # 主柜错误码
        ("__filler", c_uint32),                 # 按64位对齐的填充域

        # 资金调拨流水号
        ("allotSerialNo", c_char * OES_MAX_ALLOT_SERIALNO_LEN),
        # 错误信息
        ("errorInfo", c_char * OES_MAX_ERROR_INFO_LEN),
    ]
# -------------------------


# ===================================================================
# 现货产品信息(证券信息)的结构体定义
# ===================================================================

class OesPriceLimitT(Structure):
    """
    竞价交易的限价参数(涨停价/跌停价)定义
    """
    _fields_ = [
        ('upperLimitPrice', c_int32),           # 涨停价 (单位精确到元后四位, 即1元 = 10000)
        ('lowerLimitPrice', c_int32),           # 跌停价 (单位精确到元后四位, 即1元 = 10000)
    ]


__OES_TRD_SESS_TYPE_MAX: int = 3


# 现货产品基础信息的内容定义
__OES_STOCK_BASE_INFO_PKT = [
    # 证券代码
    ("securityId", c_char * OES_SECURITY_ID_MAX_LEN),
    ("mktId", c_uint8),                         # 市场代码 @see eOesMarketIdT

    ("productType", c_uint8),                   # 产品类型 @see eOesProductTypeT
    ("securityType", c_uint8),                  # 证券类型 @see eOesSecurityTypeT
    ("subSecurityType", c_uint8),               # 证券子类型 @see eOesSubSecurityTypeT
    ("securityLevel", c_uint8),                 # 证券级别 @see eOesSecurityLevelT
    ("securityRiskLevel", c_uint8),             # 证券风险等级 @see eOesSecurityRiskLevelT
    ("currType", c_uint8),                      # 币种 @see eOesCurrTypeT
    ("qualificationClass", c_uint8),            # 投资者适当性管理分类 @see eOesQualificationClassT

    ("securityStatus", c_uint32),               # 证券状态 @see eOesSecurityStatusT
    ("securityAttribute", c_uint32),            # 证券属性 @see eOesSecurityAttributeT
    ("suspFlag", c_uint8),                      # 禁止交易标识 (0:正常交易, 非0:禁止交易) @see eOesSecuritySuspFlagT
    ("temporarySuspFlag", c_uint8),             # 临时停牌标识 (0:未停牌, 1:已停牌)
    ("isDayTrading", c_uint8),                  # 是否支持当日回转交易 (0:不支持, 1:支持)

    ("isRegistration", c_uint8),                # 是否注册制 (0:核准制, 1:注册制)
    ("isCrdCollateral", c_uint8),               # 是否为融资融券可充抵保证金证券 (0:不可充抵保证金, 1:可充抵保证金)
    ("isCrdMarginTradeUnderlying", c_uint8),    # 是否为融资标的 (0:不是融资标的, 1:是融资标的)
    ("isCrdShortSellUnderlying", c_uint8),      # 是否为融券标的 (0:不是融券标的, 1:是融券标的)
    ("isNoProfit", c_uint8),                    # 是否尚未盈利 (0:已盈利, 1:未盈利 (仅适用于科创板和创业板产品))

    ("isWeightedVotingRights", c_uint8),        # 是否存在投票权差异 (0:无差异, 1:存在差异 (仅适用于科创板和创业板产品))
    ("isVie", c_uint8),                         # 是否具有协议控制框架 (0:没有, 1:有 (仅适用于创业板产品))
    ("isHighLiquidity", c_uint8),               # 是否为高流通性证券 (目前仅适用于融资融券业务, 融券卖出所得可买高流通性证券)
    ("isCrdCollateralTradable", c_uint8),       # 融资融券可充抵保证金证券的交易状态 (0:不可交易, 1:可交易)

    ("pricingMethod", c_uint8),                 # 计价方式 (仅适用于债券 @see eOesPricingMethodT)
    ("__STOCK_BASE_filler", c_uint8 * 3),       # 按64位对齐的填充域

    # 限价参数表 (涨/跌停价格, 数组下标为当前时段标志 @see eOesTrdSessTypeT)
    ("priceLimit", OesPriceLimitT * __OES_TRD_SESS_TYPE_MAX),
    ("priceTick", c_int32),                     # 最小报价单位 (单位精确到元后四位, 即1元 = 10000)
    ("prevClose", c_int32),                     # 前收盘价, 单位精确到元后四位, 即1元 = 10000
    ("lmtBuyMaxQty", c_int32),                  # 单笔限价买委托数量上限
    ("lmtBuyMinQty", c_int32),                  # 单笔限价买委托数量下限
    ("lmtBuyQtyUnit", c_int32),                 # 单笔限价买入单位
    ("mktBuyMaxQty", c_int32),                  # 单笔市价买委托数量上限
    ("mktBuyMinQty", c_int32),                  # 单笔市价买委托数量下限
    ("mktBuyQtyUnit", c_int32),                 # 单笔市价买入单位
    ("lmtSellMaxQty", c_int32),                 # 单笔限价卖委托数量上限
    ("lmtSellMinQty", c_int32),                 # 单笔限价卖委托数量下限
    ("lmtSellQtyUnit", c_int32),                # 单笔限价卖出单位
    ("mktSellMaxQty", c_int32),                 # 单笔市价卖委托数量上限
    ("mktSellMinQty", c_int32),                 # 单笔市价卖委托数量下限
    ("mktSellQtyUnit", c_int32),                # 单笔市价卖出单位
    ("bondInterest", c_int64),                  # 债券的每张应计利息, 单位精确到元后八位, 即应计利息1元 = 100000000
    ("parValue", c_int64),                      # 面值, 单位精确到元后四位, 即1元 = 10000
    ("repoExpirationDays", c_int32),            # 逆回购期限
    ("cashHoldDays", c_int32),                  # 占款天数

    ("auctionLimitType", c_uint8),              # 连续交易时段的有效竞价范围限制类型 @see eOesAuctionLimitTypeT
    ("auctionReferPriceType", c_uint8),         # 连续交易时段的有效竞价范围基准价类型 @see eOesAuctionReferPriceTypeT
    ("__STOCK_BASE_filler1", c_uint8 * 2),      # 按64位对齐的填充域
    ("auctionUpDownRange", c_int32),            # 连续交易时段的有效竞价范围涨跌幅度 (百分比或绝对价格, 取决于'有效竞价范围限制类型')

    ("listDate", c_int32),                      # 上市日期
    ("maturityDate", c_int32),                  # 到期日期 (仅适用于债券等有发行期限的产品)
    ("outstandingShare", c_int64),              # 总股本 (即: 总发行数量, 上证无该字段, 未额外维护时取值为0)
    ("publicFloatShare", c_int64),              # 流通股数量

    # 基础证券代码 (标的产品代码)
    ("underlyingSecurityId", c_char * OES_SECURITY_ID_MAX_LEN),
    # ETF基金申赎代码
    ("fundId", c_char * OES_SECURITY_ID_MAX_LEN),
    # 证券名称 (UTF-8 编码)
    ("securityName", c_char * OES_SECURITY_NAME_MAX_LEN),
    # 预留的备用字段
    ("__STOCK_BASE_reserve1", c_char * 80),
    # 融资融券业务专用字段
    ("creditExt", _CreditExtT),
    # 预留的备用字段
    ("__STOCK_BASE_reserve2", c_char * 48)
]


class OesStockBaseInfoT(Structure):
    """
    现货产品基础信息的结构体定义

    __OES_STOCK_BASE_INFO_PKT
    """
# -------------------------


# ===================================================================
# 证券发行信息的结构体定义
# ===================================================================

# 证券发行基础信息的内容定义
__OES_ISSUE_BASE_INFO_PKT = [
    # 证券发行代码
    ("securityId", c_char * OES_SECURITY_ID_MAX_LEN),
    ("mktId", c_uint8),                         # 市场代码 @see eOesMarketIdT
    ("securityType", c_uint8),                  # 证券类型 @see eOesSecurityTypeT
    ("subSecurityType", c_uint8),               # 证券子类型 @see eOesSubSecurityTypeT
    ("productType", c_uint8),                   # 产品类型 @see eOesProductTypeT
    ("issueType", c_uint8),                     # 发行方式 @see eOesSecurityIssueTypeT
    ("isCancelAble", c_uint8),                  # 是否允许撤单
    ("isReApplyAble", c_uint8),                 # 是否允许重复认购
    ("suspFlag", c_uint8),                      # 禁止交易标识 (0:正常交易, 非0:禁止交易) @see eOesSecuritySuspFlagT

    ("securityAttribute", c_uint32),            # 证券属性 @see eOesSecurityAttributeT
    ("isRegistration", c_uint8),                # 是否注册制 (0 核准制, 1 注册制)
    ("isNoProfit", c_uint8),                    # 是否尚未盈利 (0 已盈利, 1 未盈利 (仅适用于创业板产品))
    ("isWeightedVotingRights", c_uint8),        # 是否存在投票权差异 (0 无差异, 1 存在差异 (仅适用于创业板产品))
    ("isVie", c_uint8),                         # 是否具有协议控制框架 (0 没有, 1 有 (仅适用于创业板产品))
    ("__ISSUE_BASE_filler", c_uint8 * 8),       # 按64位对齐的填充域

    ("startDate", c_int32),                     # 发行起始日
    ("endDate", c_int32),                       # 发行结束日
    ("issuePrice", c_int32),                    # 发行价格
    ("upperLimitPrice", c_int32),               # 申购价格上限 (单位精确到元后四位, 即1元 = 10000)
    ("lowerLimitPrice", c_int32),               # 申购价格下限 (单位精确到元后四位, 即1元 = 10000)

    ("ordMaxQty", c_int32),                     # 委托最大份数
    ("ordMinQty", c_int32),                     # 委托最小份数
    ("qtyUnit", c_int32),                       # 委托份数单位

    ("issueQty", c_int64),                      # 总发行量
    ("alotRecordDay", c_int32),                 # 配股股权登记日(仅上海市场有效)
    ("alotExRightsDay", c_int32),               # 配股股权除权日(仅上海市场有效)

    # 基础证券代码 (正股代码)
    ("underlyingSecurityId", c_char * OES_SECURITY_ID_MAX_LEN),
    # 证券名称 (UTF-8 编码)
    ("securityName", c_char * OES_SECURITY_NAME_MAX_LEN),
    # 预留的备用字段
    ("__ISSUE_BASE_reserve1", c_char * 56),
    # 预留的备用字段
    ("__ISSUE_BASE_reserve2", c_char * 64)
]


class OesIssueBaseInfoT(Structure):
    """
    证券发行基础信息的结构体定义

    __OES_ISSUE_BASE_INFO_PKT
    """
# -------------------------


# ===================================================================
# ETF申赎产品基础信息的结构体定义
# ===================================================================

# ETF申赎产品基础信息定义
__OES_ETF_BASE_INFO_PKT = [
    # ETF基金申赎代码
    ("fundId", c_char * OES_SECURITY_ID_MAX_LEN),
    # ETF基金买卖代码
    ("securityId", c_char * OES_SECURITY_ID_MAX_LEN),
    # ETF基金市场代码 @see eOesMarketIdT
    ("mktId", c_uint8),

    ("securityType", c_uint8),                  # 证券类型 @see eOesSecurityTypeT
    ("subSecurityType", c_uint8),               # 证券子类型 @see eOesSubSecurityTypeT
    ("isPublishIOPV", c_uint8),                 # 是否需要发布IOPV  1: 是; 0: 否

    ("isCreationAble", c_uint8),                # 交易所/基金公司/券商端的允许申购标志  1: 是; 0: 否
    ("isRedemptionAble", c_uint8),              # 交易所/基金公司/券商端的允许赎回标志  1: 是; 0: 否
    ("isDisabled", c_uint8),                    # 券商端的禁止交易标志  1: 是; 0: 否
    ("etfAllCashFlag", c_uint8),                # ETF是否支持现金申赎标志 @see eOesEtfAllCashFlagT

    ("componentCnt", c_int32),                  # 成份证券数目
    ("creRdmUnit", c_int32),                    # 每个篮子 (最小申购、赎回单位) 对应的ETF份数, 即申购赎回单位
    ("maxCashRatio", c_int32),                  # 最大现金替代比例, 单位精确到十万分之一, 即替代比例50% = 50000
    ("nav", c_int32),                           # 前一日基金的单位净值, 单位精确到元后四位, 即1元 = 10000

    ("navPerCU", c_int64),                      # 前一日最小申赎单位净值, 单位精确到元后四位, 即1元 = 10000
    ("dividendPerCU", c_int64),                 # 红利金额, 单位精确到元后四位, 即1元 = 10000

    ("tradingDay", c_int32),                    # 当前交易日, 格式YYYYMMDD
    ("preTradingDay", c_int32),                 # 前一交易日, 格式YYYYMMDD
    ("estiCashCmpoent", c_int64),               # 每个篮子的预估现金差额, 单位精确到元后四位, 即1元 = 10000
    ("cashCmpoent", c_int64),                   # 前一日现金差额, 单位精确到元后四位, 即1元 = 10000
    ("creationLimit", c_int64),                 # 单个账户当日累计申购总额限制
    ("redemLimit", c_int64),                    # 单个账户当日累计赎回总额限制
    ("netCreationLimit", c_int64),              # 单个账户当日净申购总额限制
    ("netRedemLimit", c_int64)                  # 单个账户当日净赎回总额限制
]


class OesEtfBaseInfoT(Structure):
    """
    ETF申赎产品基础信息的结构体定义

    __OES_ETF_BASE_INFO_PKT
    """
# -------------------------


# ===================================================================
# 客户资金信息结构体定义
# ===================================================================

# 客户资金信息内容定义
__OES_CASH_ASSET_BASE_INFO_PKT = [
    # 资金账户代码
    ("cashAcctId", c_char * OES_CASH_ACCT_ID_MAX_LEN),
    # 客户代码
    ("custId", c_char * OES_CUST_ID_MAX_LEN),

    ("currType", c_uint8),                      # 币种 @see eOesCurrTypeT
    ("cashType", c_uint8),                      # 资金帐户类别(冗余自资金账户) @see eOesAcctTypeT
    ("cashAcctStatus", c_uint8),                # 资金帐户状态(冗余自资金账户) @see eOesAcctStatusT
    ("isFundTrsfDisabled", c_uint8),            # 是否禁止出入金 (仅供API查询使用)
    ("__CASH_ASSET_BASE_filler", c_uint8 * 4),  # 按64位对齐的填充域

    ("beginningBal", c_int64),                  # 期初余额, 单位精确到元后四位, 即1元 = 10000
    ("beginningAvailableBal", c_int64),         # 期初可用余额, 单位精确到元后四位, 即1元 = 10000
    ("beginningDrawableBal", c_int64),          # 期初可取余额, 单位精确到元后四位, 即1元 = 10000

    ("disableBal", c_int64),                    # 不可用金额(不可交易且不可提取, 目前仅包含上证ETF赎回所得的港市替代资金, 单位精确到元后四位, 即1元 = 10000)
    ("reversalAmt", c_int64),                   # 当前冲正金额(红冲蓝补的资金净额), 取值可以为负数(表示资金调出), 单位精确到元后四位, 即1元 = 10000
    ("manualFrzAmt", c_int64),                  # 手动冻结资金, 单位精确到元后四位, 即1元 = 10000

    ("totalDepositAmt", c_int64),               # 日中累计存入资金金额, 单位精确到元后四位, 即1元 = 10000
    ("totalWithdrawAmt", c_int64),              # 日中累计提取资金金额, 单位精确到元后四位, 即1元 = 10000
    ("withdrawFrzAmt", c_int64),                # 当前提取冻结资金金额, 单位精确到元后四位, 即1元 = 10000

    ("totalSellAmt", c_int64),                  # 日中累计 卖/赎回 获得的可用资金金额, 单位精确到元后四位, 即1元 = 10000
    ("totalBuyAmt", c_int64),                   # 日中累计 买/申购/逆回购 使用资金金额, 单位精确到元后四位, 即1元 = 10000
    ("buyFrzAmt", c_int64),                     # 当前交易冻结金额, 单位精确到元后四位, 即1元 = 10000

    ("totalFeeAmt", c_int64),                   # 日中累计交易费用金额, 单位精确到元后四位, 即1元 = 10000
    ("feeFrzAmt", c_int64),                     # 当前冻结交易费用金额, 单位精确到元后四位, 即1元 = 10000

    # 维持保证金金额, 单位精确到元后四位, 即1元 = 10000
    # 对于普通资金账户, 此字段为ETF申赎时的预估现金差额
    # 对于信用资金账户, 此字段固定为0
    # 对于衍生品资金账户, 此字段为当前维持的开仓保证金
    ("marginAmt", c_int64),
    # 在途冻结保证金金额, 单位精确到元后四位, 即1元 = 10000
    # 对于普通资金账户, 此字段为ETF申赎在途时冻结的预估现金差额
    # 对于信用资金账户, 此字段固定为0
    # 对于衍生品资金账户, 此字段为尚未成交的开仓保证金
    ("marginFrzAmt", c_int64),
]


# 客户资金回报信息的内容定义
__OES_CASH_ASSET_RPT_INFO_PKT = [
    # 当前余额 (总现金资产), 包括当前可用余额和在途冻结资金在內的汇总值, 单位精确到元后四位, 即1元 = 10000
    # - @note 可用余额请参考 '当前可用余额 (currentAvailableBal)' 字段
    ("currentTotalBal", c_int64),
    # 当前可用余额, 单位精确到元后四位, 即1元 = 10000
    # - 对于信用资金账户, 该字段表示现金还款/买融资标的可用余额
    ("currentAvailableBal", c_int64),
    # 当前可取余额, 单位精确到元后四位, 即1元 = 10000
    ("currentDrawableBal", c_int64),
    # 日中沪深结点内部划拨的累计净发生资金 (正数代表累计净划入, 负数代表累计净划出), 单位精确到元后四位, 即1元 = 10000
    ("totalInternalAllotAmt", c_int64),
    # 日中沪深结点内部划拨的在途资金 (正数代表在途划入, 负数代表在途划出), 单位精确到元后四位, 即1元 = 10000
    ("internalAllotUncomeAmt", c_int64),
    # 日中委托流量费的累计发生金额, 单位精确到元后四位, 即1元 = 10000
    ("ordTrafficFeeAmt", c_int64),
    # 预留的备用字段
    ("__CASH_ASSET_RPT_reserve", c_int64)
]


class _UnionForOesCashAssetReportT(Union):
    """
    仅适用于融资融券业务和期权业务的扩展字段
    @note 现货业务的资金回报中不会携带以下扩展字段, 不要读写和操作这些扩展字段
    """
    _fields_ = [
        ('__CASH_ASSET_EXT_reserve', c_char * 512),
        ('creditExt', OesCrdCreditAssetBaseInfoT),
        ('optionExt', _OesOptionAssetExtInfoT),
    ]


class OesCashAssetReportT(Structure):
    """
    客户资金回报结构体定义
    @note 可用余额等信息参考如下字段:
    - 总现金资产请参考 '当前余额 (currentTotalBal)' 字段
    - 可用余额请参考 '当前可用余额 (currentAvailableBal)' 字段
    - 可取余额请参考 '当前可取余额 (currentDrawableBal)' 字段
    - 信用系统现金还款/买融资标的可用余额请参考 '当前可用余额 (currentAvailableBal)' 字段
    - 信用系统买担保品可用余额请参考 '买担保品可用余额 (creditExt.buyCollateralAvailableBal)' 字段
    - 信用系统买券还券可用余额请参考 '买券还券可用余额 (creditExt.repayStockAvailableBal)' 字段

    __OES_CASH_ASSET_BASE_INFO_PKT
    __OES_CASH_ASSET_RPT_INFO_PKT
    _UnionForOesCashAssetReportT
    """
    _anonymous_ = ['_union0']
# -------------------------


# ===================================================================
# 股票持仓信息的结构体定义
# ===================================================================

# 股票持仓基础信息的内容定义
__OES_STK_HOLDING_BASE_INFO_PKT = [
    # 账户代码
    ("invAcctId", c_char * OES_INV_ACCT_ID_MAX_LEN),
    # 证券代码
    ("securityId", c_char * OES_SECURITY_ID_MAX_LEN),
    ("mktId", c_uint8),                         # 市场代码 @see eOesMarketIdT
    ("securityType", c_uint8),                  # 证券类型 @see eOesSecurityTypeT
    ("subSecurityType", c_uint8),               # 证券子类型 @see eOesSubSecurityTypeT
    ("productType", c_uint8),                   # 产品类型 @see eOesProductTypeT
    ("isCreditHolding", c_uint8),               # 信用持仓标识 (0:不是信用持仓, 1:是信用持仓)
    ("__HOLD_BASE_filler", c_uint8 * 3),        # 按64位对齐的填充域

    ("originalHld", c_int64),                   # 日初持仓
    ("originalCostAmt", c_int64),               # 日初总持仓成本 (日初持仓成本价=日初总持仓成本/日初持仓)
    ("totalBuyHld", c_int64),                   # 日中累计买入持仓
    ("totalSellHld", c_int64),                  # 日中累计卖出持仓
    ("sellFrzHld", c_int64),                    # 当前卖出冻结持仓
    ("manualFrzHld", c_int64),                  # 手动冻结持仓
    ("totalBuyAmt", c_int64),                   # 日中累计买入金额
    ("totalSellAmt", c_int64),                  # 日中累计卖出金额
    ("totalBuyFee", c_int64),                   # 日中累计买入费用
    ("totalSellFee", c_int64),                  # 日中累计卖出费用

    # 日中累计转入持仓
    # - 对于现货持仓:
    # - 表示赎回ETF获得的成份证券持仓数量, 或申购ETF获得的ETF基金持仓数量
    # - 对于信用持仓:
    # - 表示担保品划入的在途持仓数量
    ("totalTrsfInHld", c_int64),
    # 日中累计转出持仓
    # - 对于现货持仓:
    # - 表示申购ETF已使用的成份证券持仓数量, 或赎回ETF已使用的ETF基金持仓数量
    # - 对于信用持仓:
    # - 固定为0
    ("totalTrsfOutHld", c_int64),
    # 当前转出冻结持仓
    # - 对于现货持仓:
    # - 包括申购ETF在途冻结的成份证券持仓数量, 或赎回ETF在途冻结的ETF基金持仓数量
    # - 包括融资融券业务提交担保品在途冻结的持仓数量
    # - 对于信用持仓:
    # - 表示融资融券业务返还担保品在途冻结的持仓数量
    ("trsfOutFrzHld", c_int64),

    ("originalLockHld", c_int64),               # 日初锁定持仓 (日初备兑占用的持仓数量, OES内部处理时需注意对初始值进行处理)
    ("totalLockHld", c_int64),                  # 日中累计锁定持仓
    ("totalUnlockHld", c_int64),                # 日中累计解锁持仓
    ("originalAvlHld", c_int64),                # 日初可用持仓
    # 当日最大可减持额度
    # - 小于0, 不进行减持额度控制
    # - 大于或等于0, 最大可减持额度
    ("maxReduceQuota", c_int64),
]


# 股票持仓回报信息的内容定义
__OES_STK_HOLDING_RPT_INFO_PKT = [
    # 当前可卖持仓数量
    ("sellAvlHld", c_int64),

    # 当前可转换和信用系统可划出持仓数量
    # - 对于ETF申赎业务:
    # - 对于成份证券持仓, 表示申购时可以使用的成份证券数量 (现货系统)
    # - 对于ETF基金持仓, 表示赎回时可以使用的ETF基金数量 (现货系统)
    # - 对于融资融券业务:
    # - 表示信用系统可划出的担保品持仓数量 (信用系统)
    ("trsfOutAvlHld", c_int64),

    # 当前可锁定和现货系统可划出持仓数量
    # - 对于期权业务:
    # - 表示现货系统可锁定的标的证券持仓数量 (现货系统)
    # - 对于融资融券业务:
    # - 表示现货系统可划出的担保品持仓数量 (现货系统)
    # - 对于信用系统, 该字段固定为0
    ("lockAvlHld", c_int64),

    # 按64位对齐的填充域 (为兼容旧版本而保留)
    ("__STK_HOLDING_RPT_filler", c_int64),

    # 总持仓数量 (日初持仓数量+累计买入数量-累计卖出数量)
    # - 对于现货系统:
    # - 包含在途卖出冻结的持仓数量
    # - 包含在途ETF申购冻结的成份证券持仓数量
    # - 不包含在途买入数量
    # - 对于信用系统:
    # - 包含在途卖出冻结的持仓数量
    # - 包含担保品转出冻结的持仓数量
    # - 包含直接还券冻结的持仓数量
    # - 不包含在途买入数量
    # - 不包含在途担保品转入持仓数量
    # - @note 可卖持仓等相关字段:
    # - 可卖持仓请参考 '当前可卖持仓数量 (sellAvlHld)' 字段
    # - 信用系统直接还券可用持仓请参考
    # - '直接还券可用持仓数量 (repayStockDirectAvlHld)' 字段
    # - 信用系统可划出持仓请参考 '当前可转换和信用系统可划出持仓数量 (trsfOutAvlHld)' 字段
    ("sumHld", c_int64),

    # 持仓成本价
    ("costPrice", c_int64),

    # 预留的备用字段
    ("__STK_HOLDING_RPT_reserve", c_char * 32)
]


class _UnionForOesStkHoldingReport(Union):
    """
    仅适用于融资融券业务的扩展字段
    @note 现货业务的持仓回报中不会携带以下扩展字段, 不要读写和操作这些扩展字段
    """
    _fields_ = [
        # 融资融券业务专用字段
        # (即: 客户单证券融资融券负债统计信息; @note 非两融业务不要使用这些字段)
        ('creditExt', OesCrdSecurityDebtStatsBaseInfoT),
        ('__STK_HOLDING_EXT_reserve', c_char * 432)  # 预留的备用字段
    ]


class OesStkHoldingReportT(Structure):
    """
    股票持仓回报结构体定义
    @note 可卖持仓等信息参考如下字段:
    - 总持仓请参考 '总持仓数量 (sumHld)' 字段
    - 可卖持仓请参考 '当前可卖持仓数量 (sellAvlHld)' 字段
    - ETF申赎可使用的成份证券数量（申购）和ETF基金数量（赎回）
    - 请参考 '当前可转换和信用系统可划出持仓数量 (trsfOutAvlHld)' 字段
    - 现货系统可锁定（期权业务）持仓数量和现货系统可划出（两融业务）持仓数量
    - 请参考 '当前可锁定和现货系统可划出持仓数量 (lockAvlHld)' 字段
    - 信用系统直接还券可用持仓请参考
    - '直接还券可用持仓数量 (creditExt.repayStockDirectAvlHld)' 字段
    - 信用系统可划出持仓请参考 '当前可转换和信用系统可划出持仓数量 (trsfOutAvlHld)' 字段

    __OES_STK_HOLDING_BASE_INFO_PKT
    __OES_STK_HOLDING_RPT_INFO_PKT
    _UnionForOesStkHoldingReport
    """
    _anonymous_ = ['_union0']
# -------------------------


# 初始化各结构体定义
def __init_structure() -> None:
    global __OES_TRD_CNFM_LATENCY_FIELDS
    global __OES_ORD_REQ_LATENCY_FIELDS, __OES_ORD_CNFM_LATENCY_FIELDS

    if not _OES_EXPORT_LATENCY_STATS:
        __OES_ORD_REQ_LATENCY_FIELDS = []

    if not _OES_EXPORT_LATENCY_STATS:
        __OES_ORD_CNFM_LATENCY_FIELDS = []
        __OES_TRD_CNFM_LATENCY_FIELDS = []

    for cls, data in (
        (OesEtfBaseInfoT, (
                __OES_ETF_BASE_INFO_PKT, )),

        (OesStockBaseInfoT, (
                __OES_STOCK_BASE_INFO_PKT, )),

        (OesIssueBaseInfoT, (
                __OES_ISSUE_BASE_INFO_PKT, )),

        (OesStkHoldingReportT, (
                __OES_STK_HOLDING_BASE_INFO_PKT,
                __OES_STK_HOLDING_RPT_INFO_PKT,
                [('_union0', _UnionForOesStkHoldingReport)])),

        (OesLotWinningBaseInfoT, (
                __OES_LOT_WINNING_BASE_INFO_PKT, )),

        (OesFundTrsfReqT, (
                __OES_FUND_TRSF_BASE_INFO_PKT, )),

        (OesFundTrsfRejectT, (
                __OES_FUND_TRSF_BASE_INFO_PKT,
                __OES_FUND_TRSF_EXT_PKT)),

        (OesCashAssetReportT, (
                __OES_CASH_ASSET_BASE_INFO_PKT,
                __OES_CASH_ASSET_RPT_INFO_PKT,
                [('_union0', _UnionForOesCashAssetReportT)])),

        (OesOrdReqT, (
                __OES_ORD_BASE_INFO_PKT,
                __OES_ORD_REQ_LATENCY_FIELDS)),

        (OesOrdCnfmT, (
                __OES_ORD_BASE_INFO_PKT,
                __OES_ORD_REQ_LATENCY_FIELDS,
                __OES_ORD_CNFM_BASE_INFO_PKT,
                __OES_ORD_CNFM_LATENCY_FIELDS,
                __OES_ORD_CNFM_EXT_INFO_PKT)),

        (OesOrdRejectT, (
                __OES_ORD_BASE_INFO_PKT,
                __OES_ORD_REQ_LATENCY_FIELDS,
                __OES_ORD_REJECT_EXT_PKT)),

        (OesTrdCnfmT, (
                __OES_TRD_BASE_INFO_PKT,
                __OES_TRD_CNFM_BASE_INFO_PKT,
                __OES_TRD_CNFM_LATENCY_FIELDS,
                __OES_TRD_CNFM_EXT_INFO_PKT)),

        (OesOrdCancelReqT, (
                __OES_ORD_CANCEL_BASE_INFO_PKT,
                __OES_ORD_REQ_LATENCY_FIELDS)),

        (OesCrdCashRepayReportT, (
                __OES_CRD_CASH_REPAY_REQ_BASE_PKT,
                __OES_ORD_REQ_LATENCY_FIELDS,
                __OES_CRD_CASH_REPAY_REPORT_EXT_PKT)),
    ):
        cls._fields_ = reduce(lambda x, y: x + y, data, [])


__init_structure()
