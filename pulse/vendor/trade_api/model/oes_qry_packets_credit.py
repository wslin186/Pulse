# -*- coding: utf-8 -*-
"""OES两融交易查询包相关结构体"""

from functools import reduce
from ctypes import c_char, c_uint8, c_int8, c_int32, c_int64, Structure
from .oes_base_constants import (
    OES_CREDIT_DEBT_ID_MAX_LEN, OES_CUST_ID_MAX_LEN, OES_CASH_ACCT_ID_MAX_LEN,
    OES_INV_ACCT_ID_MAX_LEN, OES_SECURITY_ID_MAX_LEN,
)


# 融资融券资金头寸(可融资头寸)的基础信息内容定义
__OES_CRD_CASH_POSITION_BASE_INFO_PKT = [
    # 资金账户代码
    ("cashAcctId", c_char * OES_CASH_ACCT_ID_MAX_LEN),
    ("cashGroupNo", c_int32),                   # 头寸编号
    ("cashGroupProperty", c_uint8),             # 头寸性质 @see eOesCrdCashGroupPropertyT
    ("currType", c_uint8),                      # 币种 @see eOesCurrTypeT
    ("__CRD_CASH_POSITION_BASE_filler", c_uint8 * 2),
                                                # 按64位对齐的填充域
    ("positionAmt", c_int64),                   # 资金头寸金额 (含已用金额; 单位精确到元后四位, 即1元=10000)
    ("repaidPositionAmt", c_int64),             # 日间已归还金额 (单位精确到元后四位, 即1元=10000)
    ("usedPositionAmt", c_int64),               # 累计已用金额 (含日初已用; 单位精确到元后四位, 即1元=10000)
    ("frzPositionAmt", c_int64),                # 当前尚未成交的在途冻结金额 (单位精确到元后四位, 即1元=10000)
    ("originalBalance", c_int64),               # 期初余额 (单位精确到元后四位, 即1元=10000)
    ("originalAvailable", c_int64),             # 期初可用余额 (单位精确到元后四位, 即1元=10000)
    ("originalUsed", c_int64),                  # 期初已用金额 (期初待归还负债金额; 单位精确到元后四位, 即1元=10000)
    ("__CRD_CASH_POSITION_BASE_reserve", c_char * 32),
                                                # 预留的备用字段
]


_OesCrdCashPositionItem = [
    ('availableBalance', c_int64),              # 资金头寸剩余可融资金额 (单位精确到元后四位, 即1元=10000)
    ('custId', c_char * OES_CUST_ID_MAX_LEN),   # 客户代码
    ('totalAdjustAmt', c_int64),                # 总计调整金额 (取值可以为负数, 包括红冲蓝补金额及主柜划入金额; 单位精确到元后四位, 即1元 = 10000)
    ('__reserve', c_char * 8),                  # 预留的备用字段
]


class OesCrdCashPositionItemT(Structure):
    """
    查询到的资金头寸信息 (可融资头寸信息) 内容

    __OES_CRD_CASH_POSITION_BASE_INFO_PKT
    _OesCrdCashPositionItem
    """


# 融资融券证券头寸(可融券头寸)的基础信息内容定义
__OES_CRD_SECURITY_POSITION_BASE_INFO_PKT = [
    # 证券账户
    ("invAcctId", c_char * OES_INV_ACCT_ID_MAX_LEN),
    # 证券代码
    ("securityId", c_char * OES_SECURITY_ID_MAX_LEN),
    # 市场代码 @see eOesMarketIdT
    ("mktId", c_uint8),
    # 头寸性质 @see eOesCrdCashGroupPropertyT
    ("cashGroupProperty", c_uint8),
    # 按64位对齐的填充域
    ("__SECURITY_POSITION_BASE_filler", c_uint8 * 2),

    ("cashGroupNo", c_int32),                   # 头寸编号
    ("positionQty", c_int64),                   # 证券头寸数量 (含已用)
    ("repaidPositionQty", c_int64),             # 日间已归还数量 (当日归还不可用)
    ("usedPositionQty", c_int64),               # 累计已用数量 (含日初已用)
    ("frzPositionQty", c_int64),                # 当前尚未成交的在途冻结数量
    ("originalBalanceQty", c_int64),            # 期初数量
    ("originalAvailableQty", c_int64),          # 期初可用数量
    ("originalUsedQty", c_int64),               # 期初已用数量 (期初待归还负债数量)
    ("__SECURITY_POSITION_BASE_reserve", c_char * 32),
                                                # 预留的备用字段
]


_OesCrdSecurityPositionItem = [
    ('availablePositionQty', c_int64),          # 当前可用头寸数量
    ('custId', c_char * OES_CUST_ID_MAX_LEN),   # 客户代码
    ('__reserve', c_char * 32),                 # 保留字段
]


class OesCrdSecurityPositionItemT(Structure):
    """
    查询到的证券头寸信息 (可融券头寸信息) 内容

    __OES_CRD_SECURITY_POSITION_BASE_INFO_PKT
    _OesCrdSecurityPositionItem
    """


class OesCrdCollateralTransferOutMaxQtyItemT(Structure):
    """
    融资融券担保品可转出的最大数量信息内容
    """
    _fields_ = [
        # 客户代码
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        # 证券代码
        ("securityId", c_char * OES_SECURITY_ID_MAX_LEN),
        # 市场代码 @see eOesMarketIdT
        ("mktId", c_uint8),
        # 按64位对齐填充域
        ("__filler", c_uint8 * 7),
        # 融资融券担保品可转出的最小(下限)数量, 低于该值将转出失败
        ("collateralTransferOutMinQty", c_int64),
        # 融资融券担保品可转出的最大(上限)数量, 高于该值将转出失败
        ("collateralTransferOutMaxQty", c_int64),
        # 保留字段
        ("__reserve", c_uint8 * 32),
    ]


class OesCrdDrawableBalanceItemT(Structure):
    """
    融资融券业务最大可取资金信息内容
    """
    _fields_ = [
        # 客户代码
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        # 资金账户代码
        ("cashAcctId", c_char * OES_CASH_ACCT_ID_MAX_LEN),
        # 可取资金
        ("drawableBal", c_int64),
    ]


class OesQryCrdCreditAssetFilterT(Structure):
    """
    查询信用资产信息过滤条件
    """
    _fields_ = [
        # 客户代码, 可选项
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        # 资金账户代码, 可选项
        ("cashAcctId", c_char * OES_CASH_ACCT_ID_MAX_LEN),
        # 用户私有信息 (由客户端自定义填充, 并在应答数据中原样返回)
        ("userInfo", c_int64),
    ]


class OesQryCrdUnderlyingInfoFilterT(Structure):
    """
    查询融资融券可充抵保证金证券及融资融券标的信息过滤条件
    """
    _fields_ = [
        # 客户代码, 可选项
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        # 证券代码, 可选项
        ("securityId", c_char * OES_SECURITY_ID_MAX_LEN),
        # 市场代码, 可选项。如无需此过滤条件请使用 OES_MKT_ID_UNDEFINE @see eOesMarketIdT
        ("mktId", c_uint8),
        # 是否为融资标的 (0:未指定, 1:是融资标的, 2:不是融资标的)
        ("crdMarginTradeUnderlyingFlag", c_uint8),
        # 是否为融券标的 (0:未指定, 1:是融券标的, 2:不是融券标的)
        ("crdShortSellUnderlyingFlag", c_uint8),
        # 按64位对齐的填充域
        ("__filler", c_uint8 * 5),
        # 用户私有信息 (由客户端自定义填充, 并在应答数据中原样返回)
        ("userInfo", c_int64),
    ]


class OesQryCrdCashPositionFilterT(Structure):
    """
    查询资金头寸信息 (可融资头寸信息) 过滤条件
    """
    _fields_ = [
        # 客户代码, 可选项
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        # 资金账户代码, 可选项
        ("cashAcctId", c_char * OES_CASH_ACCT_ID_MAX_LEN),
        # 头寸性质, 可选项 @see eOesCrdCashGroupPropertyT
        ("cashGroupProperty", c_uint8),
        # 按64位对齐的填充域
        ("__filler", c_uint8 * 7),
        # 用户私有信息 (由客户端自定义填充, 并在应答数据中原样返回)
        ("userInfo", c_int64),
    ]


class OesQryCrdSecurityPositionFilterT(Structure):
    """
    查询融资融券业务证券头寸信息 (可融券头寸信息) 过滤条件
    """
    _fields_ = [
        # 客户代码, 可选项
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        # 证券账户代码, 可选项
        ("invAcctId", c_char * OES_INV_ACCT_ID_MAX_LEN),
        # 证券代码, 可选项
        ("securityId", c_char * OES_SECURITY_ID_MAX_LEN),
        # 市场代码, 可选项 @see eOesMarketIdT
        ("mktId", c_uint8),
        # 头寸性质, 可选项 @see eOesCrdCashGroupPropertyT
        ("cashGroupProperty", c_uint8),
        # 按64位对齐的填充域
        ("__filler", c_uint8 * 6),
        # 用户私有信息 (由客户端自定义填充, 并在应答数据中原样返回)
        ("userInfo", c_int64),
    ]


class OesQryCrdDebtContractFilterT(Structure):
    """
    查询融资融券合约信息过滤条件
    """
    _fields_ = [
        # 客户代码, 可选项
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        # 证券账户代码, 可选项
        ("invAcctId", c_char * OES_INV_ACCT_ID_MAX_LEN),
        # 证券代码, 可选项
        ("securityId", c_char * OES_SECURITY_ID_MAX_LEN),
        # 合约编号, 可选项
        ("debtId", c_char * OES_CREDIT_DEBT_ID_MAX_LEN),
        # 市场代码, 可选项。如无需此过滤条件请使用 OES_MKT_ID_UNDEFINE @see eOesMarketIdT
        ("mktId", c_uint8),
        # 是否仅查询未了结的融资融券合约
        ("isUnclosedOnly", c_uint8),
        # 负债类型 @see eOesCrdDebtTypeT
        ("debtType", c_uint8),
        # 历史合约标识 (0:未指定, 1:是历史合约, 2:不是历史合约)
        ("historyContractFlag", c_uint8),
        # 按64位对齐的填充域
        ("__filler", c_uint8 * 4),
        # 查询融资融券合约的起始日期 (格式为 YYYYMMDD, 形如 20160830)
        ("startDate", c_int32),
        # 查询融资融券合约的结束日期 (格式为 YYYYMMDD, 形如 20160830))
        ("endDate", c_int32),
        # 用户私有信息 (由客户端自定义填充, 并在应答数据中原样返回)
        ("userInfo", c_int64),
    ]


class OesQryCrdDebtJournalFilterT(Structure):
    """
    查询融资融券合约流水信息过滤条件
    """
    _fields_ = [
        # 客户代码, 可选项
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        # 证券账户代码, 可选项
        ("invAcctId", c_char * OES_INV_ACCT_ID_MAX_LEN),
        # 证券代码, 可选项
        ("securityId", c_char * OES_SECURITY_ID_MAX_LEN),
        # 合约编号, 可选项
        ("debtId", c_char * OES_CREDIT_DEBT_ID_MAX_LEN),
        # 市场代码, 可选项。如无需此过滤条件请使用 OES_MKT_ID_UNDEFINE @see eOesMarketIdT
        ("mktId", c_uint8),
        # 负债类型 @see eOesCrdDebtTypeT
        ("debtType", c_uint8),
        # 按64位对齐的填充域
        ("__filler", c_uint8 * 6),
        # 查询融资融券合约流水的起始日期 (目前仅支持查询当日流水, 格式为 YYYYMMDD, 形如 20160830)
        ("startDate", c_int32),
        # 查询融资融券合约流水的结束日期 (格式为 YYYYMMDD, 形如 20160830))
        ("endDate", c_int32),
        # 用户私有信息 (由客户端自定义填充, 并在应答数据中原样返回)
        ("userInfo", c_int64),
    ]


class OesQryCrdCashRepayFilterT(Structure):
    """
    查询融资融券业务直接还款信息过滤条件
    """
    _fields_ = [
        # 客户代码, 可选项
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        # 资金账户代码, 可选项
        ("cashAcctId", c_char * OES_CASH_ACCT_ID_MAX_LEN),
        # 直接还款指令流水号, 可选项
        ("clSeqNo", c_int32),
        # 客户端环境号
        ("clEnvId", c_int8),
        # 按64位对齐的填充域
        ("__filler", c_uint8 * 3),
        # 用户私有信息 (由客户端自定义填充, 并在应答数据中原样返回)
        ("userInfo", c_int64),
    ]


class OesQryCrdSecurityDebtStatsFilterT(Structure):
    """
    查询客户单证券融资融券负债统计信息过滤条件
    """
    _fields_ = [
        # 客户代码, 可选项
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        # 证券账户代码, 可选项
        ("invAcctId", c_char * OES_INV_ACCT_ID_MAX_LEN),
        # 证券代码, 可选项
        ("securityId", c_char * OES_SECURITY_ID_MAX_LEN),
        # 市场代码  @see eOesMarketIdT
        ("mktId", c_uint8),
        # 是否有融资融券负债标识 (0:未指定, 1:有融资负债(含其他负债), 2:有融券负债, 3:有融资或融券负债)
        ("hasCreditDebtFlag", c_uint8),
        # 按64位对齐的填充域
        ("__filler", c_uint8 * 6),
        # 用户私有信息 (由客户端自定义填充, 并在应答数据中原样返回)
        ("userInfo", c_int64),
    ]


class OesQryCrdExcessStockFilterT(Structure):
    """
    查询融资融券业务余券信息过滤条件
    """
    _fields_ = [
        # 客户代码, 可选项
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        # 证券账户代码, 可选项
        ("invAcctId", c_char * OES_INV_ACCT_ID_MAX_LEN),
        # 证券代码, 可选项
        ("securityId", c_char * OES_SECURITY_ID_MAX_LEN),
        # 市场代码, 可选项 @see eOesMarketIdT
        ("mktId", c_uint8),
        # 按64位对齐的填充域
        ("__filler", c_uint8 * 7),
        # 用户私有信息 (由客户端自定义填充, 并在应答数据中原样返回)
        ("userInfo", c_int64),
    ]


class OesQryCrdInterestRateFilterT(Structure):
    """
    查询融资融券息费利率过滤条件
    """
    _fields_ = [
        # 客户代码, 可选项
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        # 市场代码, 可选项。如无需此过滤条件请使用 OES_MKT_ID_UNDEFINE @see eOesMarketIdT
        ("mktId", c_uint8),
        # 买卖类型, 可选项。如无需此过滤条件请使用 OES_BS_TYPE_UNDEFINE @see eOesBuySellTypeT
        ("bsType", c_uint8),
        # 按64位对齐的填充域
        ("__filler", c_uint8 * 6),
        # 用户私有信息 (由客户端自定义填充, 并在应答数据中原样返回)
        ("userInfo", c_int64),
    ]


# 初始化结构体定义
def __init_structure() -> None:
    for cls, data in (
        (OesCrdCashPositionItemT, (
            __OES_CRD_CASH_POSITION_BASE_INFO_PKT,
            _OesCrdCashPositionItem)),

        (OesCrdSecurityPositionItemT, (
            __OES_CRD_SECURITY_POSITION_BASE_INFO_PKT,
            _OesCrdSecurityPositionItem)),
    ):
        cls._fields_ = reduce(lambda x, y: x + y, data, [])


__init_structure()
