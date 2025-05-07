# -*- coding: utf-8 -*-
"""期权基本领域模型相关结构体"""

from functools import reduce
from ctypes import c_char, c_uint8, c_int8, c_int16, c_int32, c_int64, Structure

from .oes_base_constants import (
    # spk_util.py
    UnionForUserInfo,

    OES_SECURITY_STATUS_FLAG_MAX_LEN,
    OES_CONTRACT_SYMBOL_MAX_LEN,
    OES_CONTRACT_EXCH_ID_MAX_LEN,
    OES_CUST_ID_MAX_LEN,
    OES_INV_ACCT_ID_MAX_LEN,
    OES_SECURITY_ID_MAX_LEN,
)


class OesOptSettlementConfirmReportT(Structure):
    """
    期权结算单确认回报信息的结构体定义

    __OES_OPT_SETTLEMENT_CONFIRM_BASE_PKT
    """
    _fields_ = [
        # 客户代码
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        # 用户私有信息 (由客户端自定义填充, 并在回报数据中原样返回)
        ("userInfo", UnionForUserInfo),
        ("clientId", c_int16),                  # 登录客户端编号
        ("clEnvId", c_int8),                    # 登录客户端环境号
        ("__filler2", c_int8),                  # 按64位对齐的填充域
        ("transDate", c_int32),                 # 发生日期 (格式为 YYYYMMDD, 形如 20160830)
        ("transTime", c_int32),                 # 发生时间 (格式为 HHMMSSsss, 形如 141205000)
        ("rejReason", c_int32),                 # 拒绝原因
        # 预留的备用字段
        ("__OPT_SETTLEMENT_CONFIRM_BASE_reserve", c_char * 24),
    ]


# 期权持仓基础信息的内容定义
__OES_OPT_HOLDING_BASE_INFO_PKT = [
    # 账户代码
    ("invAcctId", c_char * OES_INV_ACCT_ID_MAX_LEN),
    # 期权合约代码
    ("securityId", c_char * OES_SECURITY_ID_MAX_LEN),
    ("mktId", c_uint8),                         # 市场代码 @see eOesMarketIdT
    ("positionType", c_uint8),                  # 持仓类型 @see eOesOptPositionTypeT
    ("productType", c_uint8),                   # 产品类型 @see eOesProductTypeT
    ("securityType", c_uint8),                  # 证券类型 @see eOesSecurityTypeT
    ("subSecurityType", c_uint8),               # 证券子类型 @see eOesSubSecurityTypeT
    ("contractType", c_uint8),                  # 合约类型 (认购/认沽) @see eOesOptContractTypeT
    ("hedgeFlag", c_uint8),                     # 套保标志 (0 非套保, 1 套保)
    ("__HOLD_BASE_filler", c_uint8),            # 按64位对齐的填充域

    ("originalQty", c_int64),                   # 日初总持仓张数
    ("originalAvlQty", c_int64),                # 日初可用持仓
    ("originalCostAmt", c_int64),               # 按摊薄持仓成本价计的日初总持仓成本 (日初摊薄持仓成本价 * 日初总持仓)
    ("originalCarryingAmt", c_int64),           # 权利仓的日初持有成本 (日初持仓均价 * 日初总持仓, 不含费用)
    ("totalOpenQty", c_int64),                  # 日中累计开仓张数
    ("uncomeQty", c_int64),                     # 开仓委托未成交张数
    ("totalCloseQty", c_int64),                 # 日中累计平仓张数
    ("closeFrzQty", c_int64),                   # 平仓在途冻结张数
    ("manualFrzQty", c_int64),                  # 手动冻结张数
    ("totalInPremium", c_int64),                # 日中累计获得权利金
    ("totalOutPremium", c_int64),               # 日中累计付出权利金
    ("totalOpenFee", c_int64),                  # 日中累计开仓费用
    ("totalCloseFee", c_int64),                 # 日中累计平仓费用
    ("exerciseFrzQty", c_int64),                # 权利仓行权冻结张数
    ("positionMargin", c_int64),                # 义务仓占用保证金
    ("__OPT_HOLDING_BASE_reserve", c_char * 32) # 预留的备用字段
]


# 期权持仓回报信息的内容定义
__OES_OPT_HOLDING_RPT_INFO_PKT = [
    ("closeAvlQty", c_int64),                   # 可平仓张数 (单位: 张)
    ("exerciseAvlQty", c_int64),                # 可行权张数 (单位: 张)
    ("sumQty", c_int64),                        # 总持仓张数 (单位: 张)
    ("costPrice", c_int64),                     # 摊薄持仓成本价
    ("carryingAvgPrice", c_int64),              # 权利仓的持仓均价
    ("coveredAvlUnderlyingQty", c_int64),       # 可用的备兑持仓数量 (已锁定的标的持仓数量, 单位: 股)
    ("availableLongPositionLimit", c_int32),    # 可用的权利仓限额
    ("availableTotalPositionLimit", c_int32),   # 可用的总持仓限额
    ("availableDailyBuyOpenLimit", c_int32),    # 可用的单日买入开仓限额
    ("__OPT_HOLDING_EXT_filler2", c_int32),     # 按64位对齐的填充域
    ("__OPT_HOLDING_EXT_reserve", c_char * 32)  # 预留的备用字段
]


class OesOptHoldingReportT(Structure):
    """
    期权持仓回报结构体定义

    __OES_OPT_HOLDING_BASE_INFO_PKT
    __OES_OPT_HOLDING_RPT_INFO_PKT
    """


# 期权标的持仓基础信息的内容定义
__OES_OPT_UNDERLYING_HOLDING_BASE_PKT = [
    # 股东账户代码 (不带'888'编码的原始股东账户代码)
    ("invAcctId", c_char * OES_INV_ACCT_ID_MAX_LEN),
    # 标的证券代码
    ("underlyingSecurityId", c_char * OES_SECURITY_ID_MAX_LEN),
    # 期权市场代码 @see eOesMarketIdT
    ("mktId", c_uint8),
    # 标的市场代码 @see eOesMarketIdT
    ("underlyingMktId", c_uint8),
    # 标的证券类型 @see eOesSecurityTypeT
    ("underlyingSecurityType", c_uint8),
    # 标的证券子类型 @see eOesSubSecurityTypeT
    ("underlyingSubSecurityType", c_uint8),
    # 按64位对齐的填充域
    ("__OPT_UNDERLYING_HOLD_BASE_filler", c_uint8 * 4),

    ("originalHld", c_int64),                   # 日初标的证券的总持仓数量 (单位: 股)
    ("originalAvlHld", c_int64),                # 日初标的证券的可用持仓数量 (单位: 股)
    ("originalCoveredQty", c_int64),            # 日初备兑仓主柜实际占用的标的证券数量 (单位: 股)
    ("initialCoveredQty", c_int64),             # 日初备兑仓应占用的标的证券数量 (单位: 股)
    ("coveredQty", c_int64),                    # 当前备兑仓实际占用的标的证券数量 (单位: 股)
    ("coveredGapQty", c_int64),                 # 当前备兑仓占用标的证券的缺口数量 (单位: 股)
    ("coveredAvlQty", c_int64),                 # 当前可用于备兑开仓的标的持仓数量 (单位: 股)
    ("lockAvlQty", c_int64),                    # 当前可锁定的标的持仓数量 (单位: 股)
    ("sumHld", c_int64),                        # 标的证券总持仓, 包括当前可用持仓、不可交易持仓和在途冻结持仓在內的汇总值 (单位: 股)
    # 当日最大可减持额度
    # - 小于0, 不进行减持额度控制
    # - 大于或等于0, 最大可减持额度
    ("maxReduceQuota", c_int64),
]


class OesOptUnderlyingHoldingReportT(Structure):
    """
    期权标的持仓回报信息的结构体定义

    __OES_OPT_UNDERLYING_HOLDING_BASE_PKT
    """


class OesOptUnderlyingHoldingBaseInfoT(Structure):
    """
    期权标的持仓基础信息的结构体定义

    __OES_OPT_UNDERLYING_HOLDING_BASE_PKT
    """


class OesOptionExerciseAssignBaseT(Structure):
    """
    期权行权指派基础信息的结构体定义

    __OES_OPTION_EXERCISE_ASSIGN_BASE_PKT
    """
    _fields_ = [
        # 股东账户代码 (不带'888'编码的原始股东账户代码)
        ("invAcctId", c_char * OES_INV_ACCT_ID_MAX_LEN),
        # 期权合约代码
        ("securityId", c_char * OES_SECURITY_ID_MAX_LEN),
        # 市场代码 @see eOesMarketIdT
        ("mktId", c_uint8),
        # 持仓方向 (权利: 行权方, 义务/备兑: 被行权方) @see eOesOptPositionTypeT
        ("positionType", c_uint8),
        ("productType", c_uint8),               # 产品类型 @see eOesProductTypeT
        ("securityType", c_uint8),              # 证券类型 @see eOesSecurityTypeT
        ("subSecurityType", c_uint8),           # 证券子类型 @see eOesSubSecurityTypeT
        ("contractType", c_uint8),              # 合约类型 (认购/认沽) @see eOesOptContractTypeT
        ("deliveryType", c_uint8),              # 交割方式 @see eOesOptDeliveryTypeT
        ("__OPTION_EXERCISE_ASSIGN_filler1", c_uint8),
                                                # 按64位对齐的填充域
        ("exercisePrice", c_int32),             # 行权价格 (单位精确到元后四位, 即1元 = 10000)
        ("exerciseQty", c_int32),               # 行权张数
        ("deliveryQty", c_int64),               # 标的证券收付数量 (正数表示应收, 负数表示应付)
        ("exerciseBeginDate", c_int32),         # 行权开始日期 (格式为YYYYMMDD)
        ("exerciseEndDate", c_int32),           # 行权结束日期 (格式为YYYYMMDD)
        ("clearingDate", c_int32),              # 清算日期 (格式为YYYYMMDD)
        ("deliveryDate", c_int32),              # 交收日期 (格式为YYYYMMDD)
        ("clearingAmt", c_int64),               # 清算金额
        ("clearingFee", c_int64),               # 清算费用 (费用合计, 佣金+过户费+结算费+其它费用)
        ("settlementAmt", c_int64),             # 实际收付金额 (正数表示应收, 负数表示应付)
        ("underlyingSecurityId", c_char * OES_SECURITY_ID_MAX_LEN),
                                                # 标的证券代码
        ("underlyingMktId", c_uint8),           # 标的市场代码 @see eOesMarketIdT
        ("underlyingSecurityType", c_uint8),    # 标的证券类型 @see eOesSecurityTypeT
        ("__OPTION_EXERCISE_ASSIGN_filler3", c_uint8 * 6),
                                                # 按64位对齐的填充域
        # 期权合约名称 (UTF-8 编码)
        ("securityName", c_char * OES_CONTRACT_SYMBOL_MAX_LEN),
        # 预留的备用字段
        ("__OPTION_EXERCISE_ASSIGN_reserve", c_char * 16),
    ]


class OesOptionBaseInfoT(Structure):
    """
    期权产品基础信息的结构体定义

    __OES_OPTION_BASE_INFO_PKT
    """
    _fields_ = [
        # 期权合约代码
        ("securityId", c_char * OES_SECURITY_ID_MAX_LEN),
        ("mktId", c_uint8),                     # 市场代码 @see eOesMarketIdT
        ("productType", c_uint8),               # 产品类型 @see eOesProductTypeT
        ("securityType", c_uint8),              # 证券类型 @see eOesSecurityTypeT
        ("subSecurityType", c_uint8),           # 证券子类型 @see eOesSubSecurityTypeT
        ("contractType", c_uint8),              # 合约类型 (认购/认沽) @see eOesOptContractTypeT
        ("exerciseType", c_uint8),              # 行权方式 @see eOesOptExerciseTypeT
        ("deliveryType", c_uint8),              # 交割方式 @see eOesOptDeliveryTypeT
        ("isDayTrading", c_uint8),              # 是否支持当日回转交易 (0: 不支持; 其他: 支持)
        ("limitOpenFlag", c_uint8),             # 限制开仓标识 @see eOesOptLimitOpenFlagT
        ("suspFlag", c_uint8),                  # 禁止交易标识 (0:正常交易, 非0:禁止交易) @see eOesSecuritySuspFlagT
        ("temporarySuspFlag", c_uint8),         # 临时停牌标识 (0 未停牌, 1 已停牌)
        ("__OPTION_BASE_filler1", c_uint8 * 5), # 按64位对齐的填充域

        ("contractUnit", c_int32),              # 合约单位 (经过除权除息调整后的单位)
        ("exercisePrice", c_int32),             # 期权行权价 (经过除权除息调整后的价格, 单位精确到元后四位, 即1元 = 10000)
        ("deliveryDate", c_int32),              # 交割日期 (格式为YYYYMMDD)
        ("deliveryMonth", c_int32),             # 交割月份 (格式为YYYYMM)
        ("listDate", c_int32),                  # 上市日期 (格式为YYYYMMDD)
        ("lastTradeDay", c_int32),              # 最后交易日 (格式为YYYYMMDD)
        ("exerciseBeginDate", c_int32),         # 行权起始日期 (格式为YYYYMMDD)
        ("exerciseEndDate", c_int32),           # 行权结束日期 (格式为YYYYMMDD)
        ("contractPosition", c_int64),          # 合约持仓量 (当前合约未平仓数)
        ("prevClosePrice", c_int32),            # 合约前收盘价 (单位精确到元后四位, 即1元 = 10000)
        ("prevSettlPrice", c_int32),            # 合约前结算价 (单位精确到元后四位, 即1元 = 10000)
        ("underlyingClosePrice", c_int32),      # 标的证券前收盘价 (单位精确到元后四位, 即1元 = 10000)

        ("priceTick", c_int32),                 # 最小报价单位 (单位精确到元后四位, 即1元 = 10000)
        ("upperLimitPrice", c_int32),           # 涨停价 (单位精确到元后四位, 即1元 = 10000)
        ("lowerLimitPrice", c_int32),           # 跌停价 (单位精确到元后四位, 即1元 = 10000)
        ("buyQtyUnit", c_int32),                # 买入单位
        ("lmtBuyMaxQty", c_int32),              # 限价买数量上限 (单笔申报的最大张数)
        ("lmtBuyMinQty", c_int32),              # 限价买数量下限 (单笔申报的最小张数)
        ("mktBuyMaxQty", c_int32),              # 市价买数量上限 (单笔申报的最大张数)
        ("mktBuyMinQty", c_int32),              # 市价买数量下限 (单笔申报的最小张数)
        ("sellQtyUnit", c_int32),               # 卖出单位
        ("lmtSellMaxQty", c_int32),             # 限价卖数量上限 (单笔申报的最大张数)
        ("lmtSellMinQty", c_int32),             # 限价卖数量下限 (单笔申报的最小张数)
        ("mktSellMaxQty", c_int32),             # 市价卖数量上限 (单笔申报的最大张数)
        ("mktSellMinQty", c_int32),             # 市价卖数量下限 (单笔申报的最小张数)

        ("sellMargin", c_int64),                # 单位保证金 (上调后的今卖开每张保证金, 单位精确到元后四位, 即1元 = 10000)
        ("originalSellMargin", c_int64),        # 原始的单位保证金 (未上调的今卖开每张保证金, 单位精确到元后四位, 即1元 = 10000)
        ("marginRatioParam1", c_int32),         # 交易所保证金比例计算参数一 (单位:万分比)
        ("marginRatioParam2", c_int32),         # 交易所保证金比例计算参数二 (单位:万分比)
        ("increasedMarginRatio", c_int32),      # 券商保证金上浮比例 (单位:万分比)
        ("expireDays", c_int32),                # 临近到期天数

        # 期权合约交易所代码
        ("contractId", c_char * OES_CONTRACT_EXCH_ID_MAX_LEN),
        # 期权合约名称 (UTF-8 编码)
        ("securityName", c_char * OES_CONTRACT_SYMBOL_MAX_LEN),
        # 期权合约状态信息
        # 该字段为 8 位字符串，左起每位表示特定的含义，无定义则填空格。
        # 第 1 位: ‘0’表示可开仓，‘1’表示限制卖出开仓（不包括备兑开仓）和买入开仓。
        # 第 2 位: 预留，暂填 ‘0’
        # 第 3 位: ‘0’表示未临近到期日，‘1’表示距离到期日不足 5 个交易日。
        # 第 4 位: ‘0’表示近期未做调整，‘1’表示最近 5 个交易日内合约发生过调整。
        # 第 5 位: ‘A’表示当日新挂牌的合约，‘E’表示存续的合约。
        ("securityStatusFlag", c_char * OES_SECURITY_STATUS_FLAG_MAX_LEN),
        # 标的证券代码
        ("underlyingSecurityId", c_char * OES_SECURITY_ID_MAX_LEN),
        # 标的市场代码 @see eOesMarketIdT
        ("underlyingMktId", c_uint8),
        # 标的证券类型 @see eOesSecurityTypeT
        ("underlyingSecurityType", c_uint8),
        # 按64位对齐的填充域
        ("__OPTION_BASE_filler3", c_uint8 * 6),
    ]


class _OesOptionAssetExtInfoT(Structure):
    """
    客户期权资产拓展信息结构体
    """
    _fields_ = [
        # 日初实际占用保证金, 单位精确到元后四位, 即1元 = 10000
        ("initialMargin", c_int64),
        # 行权累计待交收冻结资金, 单位精确到元后四位, 即1元 = 10000
        ("totalExerciseFrzAmt", c_int64),
        # 待追加保证金, 单位精确到元后四位, 即1元 = 10000
        ("pendingSupplMargin", c_int64),
        # 上海市场可用限购/套保额度
        ("sseAvailablePurchaseLimit", c_int64),
        # 深圳市场可用限购/套保额度
        ("szseAvailablePurchaseLimit", c_int64),
        # 未对冲实时价格保证金, 单位精确到元后四位, 即1元 = 10000
        ("totalMarketMargin", c_int64),
        # 已对冲实时价格保证金, 单位精确到元后四位, 即1元 = 10000
        ("totalNetMargin", c_int64),
    ]


# 初始化结构体定义
def __init_structure() -> None:
    for cls, data in (
        (OesOptUnderlyingHoldingReportT, (
            __OES_OPT_UNDERLYING_HOLDING_BASE_PKT, )),

        (OesOptUnderlyingHoldingBaseInfoT, (
            __OES_OPT_UNDERLYING_HOLDING_BASE_PKT, )),

        (OesOptHoldingReportT, (
            __OES_OPT_HOLDING_BASE_INFO_PKT,
            __OES_OPT_HOLDING_RPT_INFO_PKT)),
    ):
        cls._fields_ = reduce(lambda x, y: x + y, data, [])


__init_structure()
