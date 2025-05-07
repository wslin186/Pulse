# -*- coding: utf-8 -*-
"""OES期权查询包相关结构体"""

from functools import reduce
from ctypes import c_char, c_uint8, c_int32, c_int64, Structure

from .oes_base_model_option import (
    __OES_OPT_HOLDING_BASE_INFO_PKT,
    __OES_OPT_HOLDING_RPT_INFO_PKT
)

from .oes_base_constants import (
    OES_CASH_ACCT_ID_MAX_LEN, OES_CONTRACT_EXCH_ID_MAX_LEN,
    OES_SECURITY_NAME_MAX_LEN, OES_CUST_ID_MAX_LEN,
    OES_INV_ACCT_ID_MAX_LEN, OES_SECURITY_ID_MAX_LEN,
)


_OesOptHoldingItem = [
    # 交易所合约代码
    ('contractId', c_char * OES_CONTRACT_EXCH_ID_MAX_LEN),
    # 期权合约简称
    ('contractSymbol', c_char * OES_SECURITY_NAME_MAX_LEN),
    # 昨结算价
    ('prevSettlPrice', c_int64),
]


class OesOptHoldingItemT(Structure):
    """
    查询到的期权持仓信息内容

    __OES_OPT_HOLDING_BASE_INFO_PKT
    __OES_OPT_HOLDING_RPT_INFO_PKT
    _OesOptHoldingItem
    """


class OesOptPositionLimitItemT(Structure):
    """
    查询到的期权限仓额度信息内容
    """
    _fields_ = [
        # 股东账户代码 (不带'888'编码的原始股东账户代码)
        ("invAcctId", c_char * OES_INV_ACCT_ID_MAX_LEN),
        # 标的证券代码
        ("underlyingSecurityId", c_char * OES_SECURITY_ID_MAX_LEN),
        # 市场代码 (衍生品市场) @see eOesMarketIdT
        ("mktId", c_uint8),
        # 标的市场代码 @see eOesMarketIdT
        ("underlyingMktId", c_uint8),
        # 标的证券类型 @see eOesSecurityTypeT
        ("underlyingSecurityType", c_uint8),
        # 标的证券子类型 @see eOesSubSecurityTypeT
        ("underlyingSubSecurityType", c_uint8),
        # 按64位对齐的填充域
        ("__filler1", c_uint8 * 4),

        ("longPositionLimit", c_int32),         # 权利仓限额
        ("totalPositionLimit", c_int32),        # 总持仓限额
        ("dailyBuyOpenLimit", c_int32),         # 单日买入开仓限额
        ("__filler2", c_int32),                 # 按64位对齐的填充域
        ("originalLongQty", c_int32),           # 日初权利仓持仓数量 (单位: 张)
        ("originalShortQty", c_int32),          # 日初义务仓持仓数量 (单位: 张)
        ("originalCoveredQty", c_int32),        # 日初备兑义务仓持仓数量 (单位: 张)
        ("availableLongPositionLimit", c_int32),# 未占用的权利仓限额
        ("availableTotalPositionLimit", c_int32),
                                                # 未占用的总持仓限额
        ("availableDailyBuyOpenLimit", c_int32),
                                                # 未占用的单日买入开仓限额
        ("__reserve", c_char * 8),              # 预留的备用字段
    ]


class OesOptPurchaseLimitItemT(Structure):
    """
    期权限购额度信息内容
    """
    _fields_ = [
        # 客户代码
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        # 资金账户代码
        ("cashAcctId", c_char * OES_CASH_ACCT_ID_MAX_LEN),
        # 股东账户代码 (不带'888'编码的原始股东账户代码)
        ("invAcctId", c_char * OES_INV_ACCT_ID_MAX_LEN),
        # 市场代码 (衍生品市场) @see eOesMarketIdT
        ("mktId", c_uint8),
        # 客户类别 @see eOesCustTypeT
        ("custType", c_uint8),
        # 按64位对齐的填充域
        ("__filler", c_uint8 * 6),
        # 限购额度/套保额度
        ("purchaseLimit", c_int64),
        # 日初占用的期权限购额度
        ("originalUsedPurchaseAmt", c_int64),
        # 日中累计开仓占用的期权限购额度
        ("totalOpenPurchaseAmt", c_int64),
        # 当前挂单冻结的期权限购额度
        ("frzPurchaseAmt", c_int64),
        # 日中累计平仓释放的期权限购额度
        ("totalClosePurchaseAmt", c_int64),
        # 可用限购额度/套保额度
        ("availablePurchaseLimit", c_int64),
    ]

class OesQryOptionFilterT(Structure):
    """
    查询期权产品信息过滤条件
    """
    _fields_ = [
        # 证券代码, 可选项
        ("securityId", c_char * OES_SECURITY_ID_MAX_LEN),
        # 市场代码, 可选项。如无需此过滤条件请使用 OES_MKT_ID_UNDEFINE @see eOesMarketIdT
        ("mktId", c_uint8),
        # 按64位对齐的填充域
        ("__filler", c_uint8 * 7),
        # 用户私有信息 (由客户端自定义填充, 并在应答数据中原样返回)
        ("userInfo", c_int64),
    ]


class OesQryOptHoldingFilterT(Structure):
    """查询期权持仓信息过滤条件"""
    _fields_ = [
        # 客户代码, 可选项
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        # 证券账户代码, 可选项
        ("invAcctId", c_char * OES_INV_ACCT_ID_MAX_LEN),
        # 证券代码, 可选项
        ("securityId", c_char * OES_SECURITY_ID_MAX_LEN),
        # 市场代码 @see eOesMarketIdT
        ("mktId", c_uint8),
        # 持仓类型 @see eOesOptPositionTypeT
        ("positionType", c_uint8),
        # 按64位对齐的填充域
        ("__filler", c_uint8 * 6),
        # 用户私有信息 (由客户端自定义填充, 并在应答数据中原样返回)
        ("userInfo", c_int64),
    ]


class OesQryOptUnderlyingHoldingFilterT(Structure):
    """
    查询期权标的持仓信息过滤条件
    """
    _fields_ = [
        # 客户代码, 可选项
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        # 证券账户代码, 可选项
        ("invAcctId", c_char * OES_INV_ACCT_ID_MAX_LEN),
        # 标的证券代码, 可选项
        ("underlyingSecurityId", c_char * OES_SECURITY_ID_MAX_LEN),
        # 市场代码  @see eOesMarketIdT
        ("mktId", c_uint8),
        # 证券类别  @see eOesSecurityTypeT
        ("underlyingSecurityType", c_uint8),
        # 按64位对齐的填充域
        ("__filler", c_uint8 * 6),
        # 用户私有信息 (由客户端自定义填充, 并在应答数据中原样返回)
        ("userInfo", c_int64),
    ]


class OesQryOptPositionLimitFilterT(Structure):
    """
    查询期权限仓额度信息过滤条件
    """
    _fields_ = [
        # 客户代码, 可选项
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        # 证券账户代码, 可选项
        ("invAcctId", c_char * OES_INV_ACCT_ID_MAX_LEN),
        # 标的证券代码, 可选项
        ("underlyingSecurityId", c_char * OES_SECURITY_ID_MAX_LEN),
        # 市场代码  @see eOesMarketIdT
        ("mktId", c_uint8),
        # 证券类别  @see eOesSecurityTypeT
        ("underlyingSecurityType", c_uint8),
        # 按64位对齐的填充域
        ("__filler", c_uint8 * 6),
        # 用户私有信息 (由客户端自定义填充, 并在应答数据中原样返回)
        ("userInfo", c_int64),
    ]


class OesQryOptPurchaseLimitFilterT(Structure):
    """
    查询期权限购额度信息过滤条件
    """
    _fields_ = [
        # 客户代码, 可选项
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        # 证券账户代码 (不带'888'编码的原始股东账户代码), 可选项
        ("invAcctId", c_char * OES_INV_ACCT_ID_MAX_LEN),
        # 市场代码 (衍生品市场), 可选项。如无需此过滤条件请使用 OES_MKT_ID_UNDEFINE @see eOesMarketIdT
        ("mktId", c_uint8),
        # 按64位对齐的填充域
        ("__filler", c_uint8 * 7),
        # 用户私有信息 (由客户端自定义填充, 并在应答数据中原样返回)
        ("userInfo", c_int64),
    ]


class OesQryOptExerciseAssignFilterT(Structure):
    """
    查询期权行权指派信息过滤条件
    """
    _fields_ = [
        # 客户代码, 可选项
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        # 证券账户代码, 可选项
        ("invAcctId", c_char * OES_INV_ACCT_ID_MAX_LEN),
        # 期权合约代码, 可选项
        ("securityId", c_char * OES_SECURITY_ID_MAX_LEN),
        # 市场代码 @see eOesMarketIdT
        ("mktId", c_uint8),
        # 持仓类型 @see eOesOptPositionTypeT
        ("positionType", c_uint8),
        # 按64位对齐的填充域
        ("__filler", c_uint8 * 6),
        # 用户私有信息 (由客户端自定义填充, 并在应答数据中原样返回)
        ("userInfo", c_int64),
    ]


# 初始化结构体定义
def __init_structure() -> None:

    for cls, data in (
        (OesOptHoldingItemT, (
                __OES_OPT_HOLDING_BASE_INFO_PKT,
                __OES_OPT_HOLDING_RPT_INFO_PKT,
                _OesOptHoldingItem)),
    ):
        cls._fields_ = reduce(lambda x, y: x + y, data, [])


__init_structure()
