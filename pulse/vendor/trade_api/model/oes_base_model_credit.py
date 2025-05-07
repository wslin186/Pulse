# -*- coding: utf-8 -*-
"""两融基本领域模型相关结构体"""

from functools import reduce
from ctypes import c_char, c_uint8, c_int32, c_int64, Structure
from .oes_base_constants import (
    OES_CREDIT_DEBT_ID_MAX_LEN,
    OES_CUST_ID_MAX_LEN,
    OES_CASH_ACCT_ID_MAX_LEN,
    OES_INV_ACCT_ID_MAX_LEN,
    OES_SECURITY_ID_MAX_LEN,
)


# ===================================================================
# 信用资产基础信息定义
# ===================================================================

class OesCrdCreditAssetBaseInfoT(Structure):
    """
    客户信用资产基础信息的结构体定义
    """
    _fields_ = [
        # 资金账户代码
        ("cashAcctId", c_char * OES_CASH_ACCT_ID_MAX_LEN),
        # 客户代码
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        ("currType", c_uint8),                  # 币种 @see eOesCurrTypeT
        ("cashType", c_uint8),                  # 资金帐户类别(冗余自资金账户) @see eOesAcctTypeT
        ("cashAcctStatus", c_uint8),            # 资金帐户状态(冗余自资金账户) @see eOesAcctStatusT
        ("__filler1", c_uint8 * 5),             # 按64位对齐的填充域

        # 总资产 (包含其它担保资产价值; 单位精确到元后四位, 即1元=10000)
        # - 公式: 总资产 = 现金余额(包含冻结资金在内的资金余额) + 担保证券市值(不包含买入在途,包含卖出在途和转出在途) + 其它担保资产价值
        ("totalAssetValue", c_int64),
        # 总负债 (不包括在途负债; 单位精确到元后四位, 即1元=10000)
        # - 公式: 总负债 = 融资已买入金额 + 融券已卖出证券市值 + 利息及费用(不包含未成交部分的利息及费用) + 其它负债金额
        ("totalDebtValue", c_int64),
        ("maintenaceRatio", c_int32),           # 维持担保比例 (千分比)
        ("__filler2", c_int32),                 # 按64位对齐的填充域

        ("marginAvailableBal", c_int64),        # 保证金可用余额 (单位精确到元后四位, 即1元=10000)
        ("cashBalance", c_int64),               # 现金余额 (包含融券卖出所得资金和冻结资金在内的总现金资产, 单位精确到元后四位, 即1元=10000)
        ("availableBal", c_int64),              # 可用资金 (现金还款/买融资标的可用资金; 单位精确到元后四位, 即1元=10000)
        ("drawableBal", c_int64),               # 可取资金 (单位精确到元后四位, 即1元=10000)
        ("buyCollateralAvailableBal", c_int64), # 买担保品可用资金 (买非融资标的可用资金; 单位精确到元后四位, 即1元=10000)
        ("repayStockAvailableBal", c_int64),    # 买券还券可用资金 (买券还券/买高流通性证券可用资金, 即:包含融券卖出所得资金在内的可用余额; 单位精确到元后四位, 即1元=10000)
        ("shortSellGainedAmt", c_int64),        # 融券卖出所得总额 (单位精确到元后四位, 即1元=10000)
        # 融券卖出所得可用金额 (单位精确到元后四位, 即1元=10000)
        ("shortSellGainedAvailableAmt", c_int64),

        ("totalRepaidAmt", c_int64),            # 日中累计已用于归还负债的资金总额 (卖券还款或现金归还金额; 单位精确到元后四位, 即1元=10000)
        ("repayFrzAmt", c_int64),               # 日中为归还负债而在途冻结的资金总额 (卖券还款或现金归还冻结金额; 单位精确到元后四位, 即1元=10000)

        # 融资买入授信额度 (单位精确到元后四位, 即1元=10000)
        ("marginBuyMaxQuota", c_int64),
        # 融券卖出授信额度 (单位精确到元后四位, 即1元=10000)
        ("shortSellMaxQuota", c_int64),
        # 融资融券总授信额度 (单位精确到元后四位, 即1元=10000)
        ("creditTotalMaxQuota", c_int64),

        # 融资买入已用授信额度 (单位精确到元后四位, 即1元=10000)
        # - 公式: 融资买入已用授信额度 = 融资负债金额 + 融资负债交易费用 + 在途融资金额 + 在途融资交易费用 + 其他负债金额
        ("marginBuyUsedQuota", c_int64),
        # 融资买入可用授信额度 (单位精确到元后四位, 即1元=10000)
        ("marginBuyAvailableQuota", c_int64),
        # 融券卖出已用授信额度 (单位精确到元后四位, 即1元=10000)
        # - 公式: 融券卖出已用授信额度 = 融券卖出金额 + 在途融券卖出金额
        ("shortSellUsedQuota", c_int64),
        # 融券卖出可用授信额度 (单位精确到元后四位, 即1元=10000)
        ("shortSellAvailableQuota", c_int64),
        # 专项资金头寸金额 (含已用; 单位精确到元后四位, 即1元=10000)
        ("specialCashPositionAmt", c_int64),
        # 专项资金头寸可用余额 (单位精确到元后四位, 即1元=10000)
        ("specialCashPositionAvailableBal", c_int64),
        # 公共资金头寸金额 (含已用; 单位精确到元后四位, 即1元=10000)
        ("publicCashPositionAmt", c_int64),
        # 公共资金头寸可用余额 (单位精确到元后四位, 即1元=10000)
        ("publicCashPositionAvailableBal", c_int64),
        # 证券持仓总市值 (日初持仓市值+累计买入持仓-累计卖出持仓;
        # 单位精确到元后四位, 即1元=10000)
        # - 包括自有持仓和融资买入持仓
        # - 包含在途卖出冻结的持仓市值
        # - 包含转出冻结的证券持仓市值
        # - 包含直接还券冻结的持仓市值
        # - 不包含在途买入持仓市值
        # - 不包含在途担保品转入持仓市值
        ("collateralHoldingMarketCap", c_int64),
        # 在途卖出证券持仓市值 (单位精确到元后四位, 即1元=10000)
        ("collateralUncomeSellMarketCap", c_int64),
        # 转出冻结的证券持仓市值 (单位精确到元后四位, 即1元=10000)
        ("collateralTrsfOutMarketCap", c_int64),
        # 直接还券冻结的证券持仓市值 (单位精确到元后四位, 即1元=10000)
        ("collateralRepayDirectMarketCap", c_int64),
        # 融资负债金额 (单位精确到元后四位, 即1元=10000)
        ("marginBuyDebtAmt", c_int64),
        # 融资负债交易费用 (单位精确到元后四位, 即1元=10000)
        ("marginBuyDebtFee", c_int64),
        # 融资负债利息 (单位精确到元后四位, 即1元=10000)
        ("marginBuyDebtInterest", c_int64),
        # 在途融资金额 (单位精确到元后四位, 即1元=10000)
        ("marginBuyUncomeAmt", c_int64),
        # 在途融资交易费用 (单位精确到元后四位, 即1元=10000)
        ("marginBuyUncomeFee", c_int64),
        # 在途融资利息 (单位精确到元后四位, 即1元=10000)
        ("marginBuyUncomeInterest", c_int64),
        # 融资买入证券市值 (单位精确到元后四位, 即1元=10000)
        ("marginBuyDebtMarketCap", c_int64),
        # 融资买入负债占用的保证金金额 (单位精确到元后四位, 即1元=10000)
        ("marginBuyDebtUsedMargin", c_int64),
        # 融券卖出金额 (单位精确到元后四位, 即1元=10000)
        ("shortSellDebtAmt", c_int64),
        # 融券负债交易费用 (单位精确到元后四位, 即1元=10000)
        ("shortSellDebtFee", c_int64),
        # 融券负债利息 (单位精确到元后四位, 即1元=10000)
        ("shortSellDebtInterest", c_int64),
        # 在途融券卖出金额 (单位精确到元后四位, 即1元=10000)
        ("shortSellUncomeAmt", c_int64),
        # 在途融券交易费用 (单位精确到元后四位, 即1元=10000)
        ("shortSellUncomeFee", c_int64),
        # 在途融券利息 (单位精确到元后四位, 即1元=10000)
        ("shortSellUncomeInterest", c_int64),
        # 融券卖出证券市值 (单位精确到元后四位, 即1元=10000)
        ("shortSellDebtMarketCap", c_int64),
        # 融券卖出负债占用的保证金金额 (单位精确到元后四位, 即1元=10000)
        ("shortSellDebtUsedMargin", c_int64),
        # 其他负债金额 (单位精确到元后四位, 即1元=10000)
        ("otherDebtAmt", c_int64),
        # 其他负债利息 (单位精确到元后四位, 即1元=10000)
        ("otherDebtInterest", c_int64),
        # 融资融券其他费用 (单位精确到元后四位, 即1元=10000)
        ("otherCreditFee", c_int64),
        # 融资融券专项头寸总费用 (包含融资专项头寸成本费、融券专项头寸成本费和转融通成本费; 单位精确到元后四位, 即1元=10000)
        ("creditTotalSpecialFee", c_int64),
        # 融资专项头寸成本费 (已包含在 '融资融券专项头寸总费用' 中; 单位精确到元后四位, 即1元=10000)
        ("marginBuySpecialFee", c_int64),
        # 融券专项头寸成本费 (已包含在 '融资融券专项头寸总费用' 中; 单位精确到元后四位, 即1元=10000)
        ("shortSellSpecialFee", c_int64),
        # 其它担保资产价值 (已包含在 '总资产' 中; 单位精确到元后四位, 即1元=10000)
        ("otherBackedAssetValue", c_int64),
        # 可转出资产价值 (单位精确到元后四位, 即1元=10000)
        ("trsfOutAbleAssetValue", c_int64),
        # 标的证券市值 (融资标的证券的持仓市值; 单位精确到元后四位, 即1元=10000)
        # - 不包含融资买入未归还部分的持仓
        # - 不包含在途买入和在途转出持仓
        # - 包含在途卖出持仓
        ("underlyingMarketCap", c_int64),
        # 修正资产价值 (已包含在 '总资产' 中; 单位精确到元后四位, 即1元=10000)
        ("correctAssetValue", c_int64),
        ("__reserve", c_char * 8),  # 保留字段
    ]
# -------------------------


# ===================================================================
# 融资融券可充抵保证金证券及融资融券标的基础信息定义
# ===================================================================

class OesCrdUnderlyingBaseInfoT(Structure):
    """
    融资融券可充抵保证金证券及融资融券标的基础信息的结构体定义
    """
    _fields_ = [
        # 客户代码
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        # 证券代码
        ("securityId", c_char * OES_SECURITY_ID_MAX_LEN),
        ("mktId", c_uint8),                     # 市场代码 @see eOesMarketIdT
        ("productType", c_uint8),               # 产品类型 @see eOesProductTypeT
        ("securityType", c_uint8),              # 证券类型 @see eOesSecurityTypeT
        ("subSecurityType", c_uint8),           # 证券子类型 @see eOesSubSecurityTypeT

        # 是否为融资融券可充抵保证金证券 (0:不可充抵保证金, 1:可充抵保证金)
        ("isCrdCollateral", c_uint8),
        # 是否为融资标的 (0:不是融资标的, 1:是融资标的)
        ("isCrdMarginTradeUnderlying", c_uint8),
        # 是否为融券标的 (0:不是融券标的, 1:是融券标的)
        ("isCrdShortSellUnderlying", c_uint8),
        # 融资融券可充抵保证金证券的交易状态 (0:不可交易, 1:可交易)
        ("isCrdCollateralTradable", c_uint8),
        # 是否已为个人设置融资融券担保品参数
        ("isIndividualCollateral", c_uint8),
        # 是否已为个人设置融资融券标的参数
        ("isIndividualUnderlying", c_uint8),
        # 按64位对齐的填充域
        ("__filler1", c_uint8 * 6),

        # 可充抵保证金折算率 (单位:万分比)
        ("collateralRatio", c_int32),
        # 融资买入保证金比例 (单位:万分比)
        ("marginBuyRatio", c_int32),
        # 融券卖出保证金比例 (单位:万分比)
        ("shortSellRatio", c_int32),
        # 公允价格, 大于0代表启用 (价格单位精确到元后四位, 即: 1元=10000)
        ("fairPrice", c_int32),
        # 按64位对齐的填充域
        ("__filler2", c_int32 * 2)
    ]
# -------------------------


# ===================================================================
# 融资融券合约(负债)基础信息定义
# ===================================================================

class OesCrdDebtContractReportT(Structure):
    """
    融资融券合约回报信息结构体定义

    __OES_CRD_DEBT_CONTRACT_BASE_INFO_PKT
    _OesCrdDebtContractReport
    """
    _fields_ = [
        # 合约编号
        ("debtId", c_char * OES_CREDIT_DEBT_ID_MAX_LEN),
        # 资金账户代码
        ("cashAcctId", c_char * OES_CASH_ACCT_ID_MAX_LEN),
        # 股东账户代码
        ("invAcctId", c_char * OES_INV_ACCT_ID_MAX_LEN),
        # 证券代码
        ("securityId", c_char * OES_SECURITY_ID_MAX_LEN),

        ("mktId", c_uint8),                     # 市场代码 @see eOesMarketIdT
        ("securityType", c_uint8),              # 证券类型 @see eOesSecurityTypeT
        ("subSecurityType", c_uint8),           # 证券子类型 @see eOesSubSecurityTypeT
        ("securityProductType", c_uint8),       # 证券的产品类型 @see eOesProductTypeT
        ("debtType", c_uint8),                  # 负债类型 @see eOesCrdDebtTypeT
        ("debtStatus", c_uint8),                # 负债状态 @see eOesCrdDebtStatusT
        ("originalDebtStatus", c_uint8),        # 期初负债状态 @see eOesCrdDebtStatusT
        ("debtRepayMode", c_uint8),             # 负债归还模式 @see eOesCrdDebtRepayModeT

        ("ordDate", c_int32),                   # 委托日期 (格式为 YYYYMMDD, 形如 20160830)
        ("ordPrice", c_int32),                  # 委托价格 (单位精确到元后四位, 即1元=10000)
        ("ordQty", c_int32),                    # 委托数量
        ("trdQty", c_int32),                    # 成交数量

        ("ordAmt", c_int64),                    # 委托金额 (单位精确到元后四位, 即1元=10000)
        ("trdAmt", c_int64),                    # 成交金额 (单位精确到元后四位, 即1元=10000)
        ("trdFee", c_int64),                    # 成交费用 (仅用于展示, 负债部分参见合约手续费(currentDebtFee)字段, 单位精确到元后四位, 即1元=10000)

        ("currentDebtAmt", c_int64),            # 实时合约金额 (单位精确到元后四位, 即1元=10000)
        ("currentDebtFee", c_int64),            # 实时合约手续费 (单位精确到元后四位, 即1元=10000)
        ("currentDebtInterest", c_int64),       # 实时合约利息 (含罚息. 单位精确到元后四位, 即1元=10000)
        ("currentDebtQty", c_int32),            # 实时合约数量

        ("uncomeDebtQty", c_int32),             # 在途冻结数量
        ("uncomeDebtAmt", c_int64),             # 在途冻结金额 (单位精确到元后四位, 即1元=10000)
        ("uncomeDebtFee", c_int64),             # 在途冻结手续费 (单位精确到元后四位, 即1元=10000)
        ("uncomeDebtInterest", c_int64),        # 在途冻结利息 (单位精确到元后四位, 即1元=10000)

        # 累计已归还金额 (单位精确到元后四位, 即1元=10000)
        # - 对于融资，是归还的融资负债金额
        # - 对于融券，是归还的融券数量*归还时的成交价格 (即实际归还金额)
        ("totalRepaidAmt", c_int64),
        # 累计已归还手续费 (仅包含当日归还. 单位精确到元后四位, 即1元=10000)
        ("totalRepaidFee", c_int64),
        # 累计已归还利息 (单位精确到元后四位, 即1元=10000)
        ("totalRepaidInterest", c_int64),

        # 累计已归还数量
        # - 对于融券，是归还的融券负债数量
        # - 对于融资，是归还的融资金额/归还时该证券最新价格
        ("totalRepaidQty", c_int32),
        # 按64位对齐的填充域
        ("__CRD_DEBT_CONTRACT_BASE_filler2", c_int32),

        ("originalDebtAmt", c_int64),           # 期初待归还金额 (单位精确到元后四位, 即1元=10000)
        ("originalDebtFee", c_int64),           # 期初待归还手续费 (单位精确到元后四位, 即1元=10000)
        ("originalDebtInterest", c_int64),      # 期初待归还利息 (含罚息. 单位精确到元后四位, 即1元=10000)
        ("originalDebtQty", c_int32),           # 期初待归还数量

        # 期初已归还数量
        # - 对于融券，是归还的融券负债数量
        # - 对于融资，是归还的融资金额/归还时该证券最新价格
        ("originalRepaidQty", c_int32),
        # 期初已归还金额 (单位精确到元后四位, 即1元=10000)
        # - 对于融资，是归还的融资负债金额
        # - 对于融券，是归还的融券数量*归还时成交价格
        ("originalRepaidAmt", c_int64),
        # 期初已归还利息 (含罚息. 单位精确到元后四位, 即1元=10000)
        ("originalRepaidInterest", c_int64),
        # 罚息 (仅供展示, 已在利息中体现. 单位精确到元后四位, 即1元=10000)
        ("punishInterest", c_int64),

        ("marginRatio", c_int32),               # 保证金比例 (单位:万分比)
        ("interestRate", c_int32),              # 融资利率/融券费率 (单位精确到万分之一, 即费率8.36% = 836)
        ("repayEndDate", c_int32),              # 负债截止日期 (格式为 YYYYMMDD, 形如 20160830)
        ("cashGroupNo", c_int32),               # 头寸编号
        ("postponeTimes", c_int32),             # 展期次数
        ("postponeStatus", c_uint8),            # 展期状态 @see eOesCrdDebtPostponeStatusT
        # 按64位对齐的填充域
        ("__CRD_DEBT_CONTRACT_BASE_filler3", c_uint8 * 3),

        # 预留的备用字段
        ("__CREDIT_DEBT_BASE_reserve", c_char * 32),
        # 同一证券所有融券合约的合计可归还负债数量
        # - 公式: 同一证券合计可归还负债数量 = 日初融券负债数量 - 当日已归还融券数量 - 在途归还融券数量
        ('securityRepayableDebtQty', c_int64),
        # 该融券合约的当前可归还负债数量
        # - 公式: 合约当前可归还负债数量 = 实时合约数量 - 归还指定合约的在途归还数量
        # - @note 实际允许归还的负债数量, 为该融券合约可归还负债数量与对应证券可归还负债数量的较小者
        ('contractRepayableDebtQty', c_int32),
        # 按64位对齐的填充域
        ('__filler', c_int32),
        # 保留字段
        ('__reserve', c_char * 32)
    ]
# -------------------------


# ===================================================================
# 融资融券合约流水信息定义
# ===================================================================

# 融资融券合约负债流水的基础信息内容定义
# @note    记录合约负债变动流水, 包括: 开仓流水、归还流水、以及合约展期流水
#          - 对于归还流水, 发生金额、发生费用、发生利息、发生证券数量为负数
#          - 对于开仓流水, 对应数据为正数
#          - 对于合约展期流水, 发生金额、发生费用等数据为0
__OES_CRD_DEBT_JOURNAL_BASE_INFO_PKT = [
    # 合约编号
    ("debtId", c_char * OES_CREDIT_DEBT_ID_MAX_LEN),
    # 资金账户代码
    ("cashAcctId", c_char * OES_CASH_ACCT_ID_MAX_LEN),
    # 股东账户代码
    ("invAcctId", c_char * OES_INV_ACCT_ID_MAX_LEN),
    # 证券代码
    ("securityId", c_char * OES_SECURITY_ID_MAX_LEN),

    ("mktId", c_uint8),                         # 市场代码 @see eOesMarketIdT
    ("debtType", c_uint8),                      # 负债类型 @see eOesCrdDebtTypeT
    ("journalType", c_uint8),                   # 流水类型 @see eOesCrdDebtJournalTypeT
    ("mandatoryFlag", c_uint8),                 # 强制标志 @see eOesOrdMandatoryFlagT
    ("seqNo", c_int32),                         # 同一融资融券合约的负债流水的顺序号

    ("occurAmt", c_int64),                      # 发生金额 (不含息费; 单位精确到元后四位, 即1元=10000)
    ("occurFee", c_int64),                      # 发生费用 (单位精确到元后四位, 即1元=10000)
    ("occurInterest", c_int64),                 # 发生利息 (单位精确到元后四位, 即1元=10000)
    ("occurQty", c_int32),                      # 发生证券数量
    ("postQty", c_int32),                       # 后余证券数量
    ("postAmt", c_int64),                       # 后余金额 (不含息费; 单位精确到元后四位, 即1元=10000)
    ("postFee", c_int64),                       # 后余费用 (单位精确到元后四位, 即1元=10000)
    ("postInterest", c_int64),                  # 后余利息 (单位精确到元后四位, 即1元=10000)

    # 融券合约流水的理论发生金额 (单位精确到元后四位, 即1元=10000)
    # - 开仓流水中等同于发生金额, 即成交金额
    # - 归还流水中为对应于合约开仓价格的理论上的发生金额
    ("shortSellTheoryOccurAmt", c_int64),
    # 归还息费时使用融券卖出所得抵扣的金额 (单位精确到元后四位, 即1元=10000)
    ("useShortSellGainedAmt", c_int64),
    # 委托日期 (格式为 YYYYMMDD, 形如 20160830)
    ("ordDate", c_int32),
    # 委托时间 (格式为 HHMMSSsss, 形如 141205000)
    ("ordTime", c_int32),
    # 预留的备用字段
    ("__CRD_DEBT_JOURNAL_BASE_reserve", c_char * 32)
]


class OesCrdDebtJournalBaseInfoT(Structure):
    """
    融资融券合约负债流水的基础信息结构体定义

    __OES_CRD_DEBT_JOURNAL_BASE_INFO_PKT
    """


class OesCrdDebtJournalReportT(Structure):
    """
    融资融券合约流水变动信息回报结构体定义

    __OES_CRD_DEBT_JOURNAL_BASE_INFO_PKT
    """
# -------------------------


# ===================================================================
# 客户单证券融资融券负债统计基础信息定义
# ===================================================================

class OesCrdSecurityDebtStatsBaseInfoT(Structure):
    """
    客户单证券融资融券负债统计基础信息的结构体定义
    """
    _fields_ = [
        # 股东账户代码
        ("invAcctId", c_char * OES_INV_ACCT_ID_MAX_LEN),
        # 证券代码
        ("securityId", c_char * OES_SECURITY_ID_MAX_LEN),
        ("mktId", c_uint8),                     # 市场代码 @see eOesMarketIdT
        ("productType", c_uint8),               # 产品类型 @see eOesProductTypeT
        ("securityType", c_uint8),              # 证券类型 @see eOesSecurityTypeT
        ("subSecurityType", c_uint8),           # 证券子类型 @see eOesSubSecurityTypeT

        # 是否为融资融券可充抵保证金证券 (0:不可充抵保证金, 1:可充抵保证金)
        ("isCrdCollateral", c_uint8),
        # 是否为融资标的 (0:不是融资标的, 1:是融资标的)
        ("isCrdMarginTradeUnderlying", c_uint8),
        # 是否为融券标的 (0:不是融券标的, 1:是融券标的)
        ("isCrdShortSellUnderlying", c_uint8),
        # 融资融券可充抵保证金证券的交易状态 (0:不可交易, 1:可交易)
        ("isCrdCollateralTradable", c_uint8),
        ("collateralRatio", c_int32),           # 可充抵保证金折算率 (单位:万分比)
        ("marginBuyRatio", c_int32),            # 融资买入保证金比例 (单位:万分比)
        ("shortSellRatio", c_int32),            # 融券卖出保证金比例 (单位:万分比)
        # 市值计算使用的证券价格, 等价于最新价或公允价, 取决于是否开启公允价格; 价格单位精确到元后四位, 即1元=10000
        ("marketCapPrice", c_int32),

        # 可卖持仓数量
        ("sellAvlHld", c_int64),
        # 可划出持仓数量 (可充抵保证金证券(担保品)可划出数量)
        ("trsfOutAvlHld", c_int64),
        # 直接还券可用持仓数量
        ("repayStockDirectAvlHld", c_int64),
        # 同一证券所有融券合约的合计待归还负债数量
        # - 公式: 同一证券合计待归还负债数量 =
        # 日初融券负债数量 - 当日已归还融券数量 - 在途归还融券数量
        ("shortSellRepayableDebtQty", c_int64),
        # 专项证券头寸数量 (含已用)
        ("specialSecurityPositionQty", c_int64),
        # 专项证券头寸已用数量 (含尚未成交的在途冻结数量)
        ("specialSecurityPositionUsedQty", c_int64),
        # 专项证券头寸可用数量
        # - 当可用头寸低于有效数量下限(卖委托数量下限)时该字段将返回0
        # - @note 实际剩余的未使用头寸数量可通过如下公式计算:
        # 实际剩余的可用头寸数量 = 专项证券头寸数量 - 专项证券头寸已用数量
        ("specialSecurityPositionAvailableQty", c_int64),
        # 公共证券头寸数量 (含已用)
        ("publicSecurityPositionQty", c_int64),
        # 公共证券头寸可用数量
        ("publicSecurityPositionAvailableQty", c_int64),
        # 总持仓数量 (日初持仓数量+累计买入数量-累计卖出数量)
        # - 包括自有持仓和融资买入持仓
        # - 包含在途卖出冻结的持仓数量
        # - 包含转出冻结的持仓数量
        # - 包含直接还券冻结的持仓数量
        # - 不包含在途买入数量
        # - 不包含在途担保品转入持仓数量
        ("collateralHoldingQty", c_int64),
        # 在途买入数量 (不包括融资买入在途数量)
        ("collateralUncomeBuyQty", c_int64),
        # 在途转入持仓数量 (包含已确认和未确认数量, 不包含已撤单数量)
        ("collateralUncomeTrsfInQty", c_int64),
        # 在途卖出冻结的持仓数量
        ("collateralUncomeSellQty", c_int64),
        # 转出冻结的持仓数量 (包含已确认和未确认数量, 不包含已撤单数量)
        ("collateralTrsfOutQty", c_int64),
        # 直接还券冻结的持仓数量 (包含已确认和未确认数量, 不包含已撤单/废单数量)
        ("collateralRepayDirectQty", c_int64),
        # 融资负债金额 (不包括已还; 单位精确到元后四位, 即1元=10000)
        ("marginBuyDebtAmt", c_int64),
        # 融资交易费用 (不包括已还; 单位精确到元后四位, 即1元=10000)
        ("marginBuyDebtFee", c_int64),
        # 融资负债利息 (包括罚息, 不包括已还; 单位精确到元后四位, 即1元=10000)
        ("marginBuyDebtInterest", c_int64),
        # 融资负债数量 (不包括已还)
        ("marginBuyDebtQty", c_int64),
        # 在途融资买入金额, 单位精确到元后四位, 即1元 = 10000
        ("marginBuyUncomeAmt", c_int64),
        # 在途融资交易费用, 单位精确到元后四位, 即1元 = 10000
        ("marginBuyUncomeFee", c_int64),
        # 在途融资利息, 单位精确到元后四位, 即1元 = 10000
        ("marginBuyUncomeInterest", c_int64),
        # 在途融资数量
        ("marginBuyUncomeQty", c_int64),
        # 日初融资负债金额 (日初融资余额, 不包括日初已还)
        ("marginBuyOriginDebtAmt", c_int64),
        # 日初融资负债数量 (不包括日初已还)
        ("marginBuyOriginDebtQty", c_int64),
        # 当日已归还融资金额 (日中发生的归还金额, 不包括日初已还)
        ("marginBuyRepaidAmt", c_int64),
        # 当日已归还融资数量 (对应于合约开仓价格的理论上的已归还融资数量)
        ("marginBuyRepaidQty", c_int64),
        # 融券负债金额 (不包括已还; 单位精确到元后四位, 即1元=10000)
        ("shortSellDebtAmt", c_int64),
        # 融券交易费用 (不包括已还; 单位精确到元后四位, 即1元=10000)
        ("shortSellDebtFee", c_int64),
        # 融券负债利息 (包括罚息, 不包括已还; 单位精确到元后四位, 即1元=10000)
        ("shortSellDebtInterest", c_int64),
        # 融券负债数量 (不包括已还)
        ("shortSellDebtQty", c_int64),
        # 在途融券卖出金额, 单位精确到元后四位, 即1元 = 10000
        ("shortSellUncomeAmt", c_int64),
        # 在途融券交易费用, 单位精确到元后四位, 即1元 = 10000
        ("shortSellUncomeFee", c_int64),
        # 在途融券利息, 单位精确到元后四位, 即1元 = 10000
        ("shortSellUncomeInterest", c_int64),
        ("shortSellUncomeQty", c_int64),  # 在途融券数量
        # 日初融券负债数量 (日初融券余量, 不包括日初已还)
        ("shortSellOriginDebtQty", c_int64),
        # 当日已归还融券数量 (日中发生的归还数量, 不包括日初已还)
        ("shortSellRepaidQty", c_int64),
        # 在途归还融券数量
        ("shortSellUncomeRepaidQty", c_int64),
        # 当日已归还融券金额 (按开仓价格计算的理论上已归还融券金额; 单位精确到元后四位, 即1元=10000)
        ("shortSellRepaidAmt", c_int64),
        # 当日实际归还融券金额 (按成交价计算的当日实际归还融券金额; 单位精确到元后四位, 即1元=10000)
        ("shortSellRealRepaidAmt", c_int64),
        # '其它负债'的负债金额 (不包括已还; 单位精确到元后四位, 即1元=10000)
        ("otherDebtAmt", c_int64),
        # '其它负债'利息 (包括罚息, 不包括已还; 单位精确到元后四位, 即1元=10000)
        ("otherDebtInterest", c_int64),
        # 保留字段
        ("__reserve", c_char * 32)
    ]
# -------------------------


# ===================================================================
# 余券基础信息定义
# ===================================================================

# 融资融券余券信息的基础信息内容定义
class OesCrdExcessStockBaseInfoT(Structure):
    """融资融券余券基础信息的结构体定义"""
    _fields_ = [
        ("custId", c_char * OES_CUST_ID_MAX_LEN),  # 客户代码
        ("invAcctId", c_char * OES_INV_ACCT_ID_MAX_LEN),  # 证券账户代码
        ("securityId", c_char * OES_SECURITY_ID_MAX_LEN),  # 证券代码
        ("mktId", c_uint8),  # 市场代码  @see eOesMarketIdT
        ("__filler", c_uint8 * 7),  # 按64位对齐的填充域
        ("originExcessStockQty", c_int64),  # 日初余券数量
        ("excessStockTotalQty", c_int64),  # 余券数量 (日初余券数量 + 日中余券数量)
        # 余券已划转数量 (包含已确认和未确认数量, 不包含已撤单数量)
        ("excessStockUncomeTrsfQty", c_int64),
        ("excessStockTrsfAbleQty", c_int64),  # 余券可划转数量
        ("__reserve", c_char * 32),  # 保留字段
    ]
# -------------------------


# ===================================================================
# 融资融券业务扩展的结构体定义
# ===================================================================

class _CreditExtT(Structure):
    _fields_ = [
        ("collateralRatio", c_int32),           # 可充抵保证金折算率 (单位:万分比)
        ("marginBuyRatio", c_int32),            # 融资买入保证金比例 (单位:万分比)
        ("shortSellRatio", c_int32),            # 融券卖出保证金比例 (单位:万分比)
        ("fairPrice", c_int32),                 # 公允价格, 大于0代表启用 (价格单位精确到元后四位, 即: 1元=10000)
    ]
# -------------------------


# 初始化结构体定义
def __init_structure() -> None:
    for cls, data in (
        (OesCrdDebtJournalReportT, (__OES_CRD_DEBT_JOURNAL_BASE_INFO_PKT, )),
        (OesCrdDebtJournalBaseInfoT, (__OES_CRD_DEBT_JOURNAL_BASE_INFO_PKT, )),
    ):
        cls._fields_ = reduce(lambda x, y: x + y, data, [])


__init_structure()
