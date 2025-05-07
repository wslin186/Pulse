# -*- coding: utf-8 -*-
"""OES现货查询相关包结构体定义"""

from ctypes import (
    c_char, c_uint8, c_int8, c_int16, c_uint32, c_int32,
    c_uint64, c_int64, Structure, Union
)
from .oes_base_constants import (
    OES_CUST_ID_MAX_LEN, OES_SECURITY_ID_MAX_LEN, OES_INV_ACCT_ID_MAX_LEN,
    OES_SECURITY_NAME_MAX_LEN, OES_CASH_ACCT_ID_MAX_LEN, OES_CLIENT_NAME_MAX_LEN,
    OES_BANK_NO_MAX_LEN, OES_CUST_LONG_NAME_MAX_LEN, OES_CLIENT_DESC_MAX_LEN,
    OES_MAX_CUST_PER_CLIENT, OES_CUST_NAME_MAX_LEN, OES_BROKER_NAME_MAX_LEN,
    OES_BROKER_PHONE_MAX_LEN, OES_BROKER_WEBSITE_MAX_LEN, OES_VER_ID_MAX_LEN
)


class OesMarketStateItemT(Structure):
    """
    市场状态信息内容
    """
    _fields_ = (
        ('exchId', c_uint8),                    # 交易所代码 @see eOesExchangeIdT
        ('platformId', c_uint8),                # 交易平台类型 @see eOesPlatformIdT
        ('mktId', c_uint8),                     # 市场代码 @see eOesMarketIdT
        ('mktState', c_uint8),                  # 市场状态 @see eOesMarketStateT
        ('__filler', c_uint8 * 4),              # 按64位对齐的填充域
    )

OesMarketStateInfoT = OesMarketStateItemT


class OesCommissionRateItemT(Structure):
    """
    客户佣金信息内容定义
    """
    _fields_ = [
        # 客户代码
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        # 证券代码
        ("securityId", c_char * OES_SECURITY_ID_MAX_LEN),
        ("mktId", c_uint8),                     # 市场 @see eOesMarketIdT
        ("securityType", c_uint8),              # 证券类别 @see eOesSecurityTypeT
        ("subSecurityType", c_uint8),           # 证券子类别 @see eOesSubSecurityTypeT
        ("bsType", c_uint8),                    # 买卖类型 @see eOesBuySellTypeT
        ("feeType", c_uint8),                   # 费用标识 @see eOesFeeTypeT
        ("currType", c_uint8),                  # 币种 @see eOesCurrTypeT
        ("calcFeeMode", c_uint8),               # 计算模式 @see eOesCalcFeeModeT
        ("__filler", c_uint8),                  # 按64位对齐的填充域
        ("feeRate", c_int64),                   # 费率, 单位精确到千万分之一, 即费率0.02% = 2000
        ("minFee", c_int32),                    # 最低费用, 大于0时有效 (单位：万分之一元)
        ("maxFee", c_int32),                    # 最高费用, 大于0时有效 (单位：万分之一元)
    ]

# 融资融券息费利率内容定义
OesCrdInterestRateItemT = OesCommissionRateItemT


class OesEtfComponentItemT(Structure):
    """
    ETF基金成份证券信息内容

    __OES_ETF_COMPONENT_BASE_INFO_PKT
    _OesEtfComponentItem
    """
    _fields_ = [
        # ETF基金申赎代码
        ("fundId", c_char * OES_SECURITY_ID_MAX_LEN),
        # 成份证券代码
        ("securityId", c_char * OES_SECURITY_ID_MAX_LEN),
        ("mktId", c_uint8),                     # 成份证券市场代码 @see eOesMarketIdT
        ("fundMktId", c_uint8),                 # ETF基金市场代码 @see eOesMarketIdT
        ("subFlag", c_uint8),                   # 现金替代标识 @see eOesEtfSubFlagT
        # 成份证券的证券类型(仅对沪市、深市成分证券有效) @see eOesSecurityTypeT
        ("securityType", c_uint8),
        # 成份证券的证券子类型(仅对沪市、深市成分证券有效) @see eOesSubSecurityTypeT
        ("subSecurityType", c_uint8),
        # 是否是作为申赎对价的成份证券
        # @note 注意事项:
        # - 非申赎对价的成份证券信息仅供参考, 申赎时不能对该类成份证券进行股份计算或现金替代处理。
        # - 例如: 深交所跨市场ETF中的沪市成份证券信息就属于非申赎对价的成份证券信息,
        #         对深交所跨市场ETF进行申赎时应使用 159900 虚拟成份券进行沪市成份证券份额的现金替代处理
        ("isTrdComponent", c_uint8),
        # 按64位对齐的填充域
        ("__ETF_COMPONENT_BASE_filler", c_uint8 * 2),
        # 前收盘价格(仅对沪市、深市成分证券有效), 单位精确到元后四位, 即1元 = 10000
        ("prevClose", c_int32),
        # 成份证券数量
        ("qty", c_int32),
        # 申购溢价比例, 单位精确到十万分之一, 即溢价比例10% = 10000
        ("premiumRatio", c_int32),
        # 赎回折价比例, 单位精确到十万分之一, 即折价比例10% = 10000
        ("discountRatio", c_int32),
        # 申购替代金额, 单位精确到元后四位, 即1元 = 10000
        ("creationSubCash", c_int64),
        # 赎回替代金额, 单位精确到元后四位, 即1元 = 10000
        ("redemptionSubCash", c_int64),
        # 成份证券名称
        ('securityName', c_char * OES_SECURITY_NAME_MAX_LEN),
        # 预留的备用字段
        ('__reserve', c_char * 96),
    ]


class OesCashAcctOverviewT(Structure):
    """
    客户端总览信息 - 资金账户信息总览
    """
    _fields_ = [
        # 资金账户代码
        ("cashAcctId", c_char * OES_CASH_ACCT_ID_MAX_LEN),
        # 客户代码
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        # 银行代码
        ("bankId", c_char * OES_BANK_NO_MAX_LEN),

        ("isValid", c_uint8),                   # 资金账户是否有效标识
        ("cashType", c_uint8),                  # 资金账户类别 @see eOesAcctTypeT
        ("cashAcctStatus", c_uint8),            # 资金账户状态 @see eOesAcctStatusT
        ("currType", c_uint8),                  # 币种类型 @see eOesCurrTypeT
        ("isFundTrsfDisabled", c_uint8),        # 出入金是否禁止标识
        ("__filler", c_uint8 * 3),              # 按64位对齐的填充域
        ("__reserve", c_char * 64),             # 备用字段
    ]


class OesInvAcctOverviewT(Structure):
    """
    客户端总览信息 - 股东账户信息总览
    """
    _fields_ = [
        # 客户代码
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        # 股东账户代码
        ("invAcctId", c_char * OES_INV_ACCT_ID_MAX_LEN),

        ("isValid", c_uint8),                   # 股东账户是否有效标识
        ("mktId", c_uint8),                     # 市场 @see eOesMarketIdT
        ("acctType", c_uint8),                  # 账户类型 @see eOesAcctTypeT
        ("status", c_uint8),                    # 账户状态 @see eOesAcctStatusT
        ("ownerType", c_uint8),                 # 股东账户的所有者类型 @see eOesOwnerTypeT
        ("optInvLevel", c_uint8),               # 期权投资者级别 @see eOesOptInvLevelT
        ("isTradeDisabled", c_uint8),           # 是否禁止交易 (仅供API查询使用)
        ("__filler1", c_uint8),                 # 按64位对齐的填充域

        ("limits", c_uint64),                   # 证券账户权限限制 @see eOesLimitT
        ("permissions", c_uint64),              # 股东权限/客户权限 @see eOesTradingPermissionT
        ("pbuId", c_int32),                     # 席位号
        ("subscriptionQuota", c_int32),         # 主板权益 (新股/配股认购限额)
        ("kcSubscriptionQuota", c_int32),       # 科创板权益 (新股/配股认购限额)
        # 风险警示板证券单日买入数量限制
        ("riskWarningSecurityBuyQtyLimit", c_int32),
        ("trdOrdCnt", c_int32),                 # 当日累计有效交易类委托笔数统计
        ("nonTrdOrdCnt", c_int32),              # 当日累计有效非交易类委托笔数统计
        ("cancelOrdCnt", c_int32),              # 当日累计有效撤单笔数统计
        ("oesRejectOrdCnt", c_int32),           # 当日累计被OES拒绝的委托笔数统计
        ("exchRejectOrdCnt", c_int32),          # 当日累计被交易所拒绝的委托笔数统计
        ("trdCnt", c_int32),                    # 当日累计成交笔数统计
        ("__reserve", c_char * 64),             # 备用字段
    ]


class OesCustOverviewT(Structure):
    """
    客户端总览信息 - 客户信息总览
    """
    _fields_ = [
        # 客户代码
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        ("custType", c_uint8),                  # 客户类型 @see eOesCustTypeT
        ("status", c_uint8),                    # 客户状态 (0:正常, 非0:不正常)
        ("riskLevel", c_uint8),                 # OES风险等级 @see eOesSecurityRiskLevelT
        ("originRiskLevel", c_uint8),           # 客户原始风险等级
        ("institutionFlag", c_uint8),           # 机构标志 (0:个人投资者, 1:机构投资者)
        ("investorClass", c_uint8),             # 投资者分类 @see eOesInvestorClassT
        ("optSettlementCnfmFlag", c_uint8),     # 期权账户结算单确认标志 (0:未确认, 1:已确认)
        ("__CUST_BASE_filler1", c_uint8),       # 按64位对齐的填充域

        ("branchId", c_int32),                  # 交易营业部代码
        ("__CUST_BASE_filler2", c_uint32),      # 按64位对齐的填充域

        ('cashAcct', OesCashAcctOverviewT),     # 资金账户信息
        ('sseInvAcct', OesInvAcctOverviewT),    # 上海股东账户信息
        ('szseInvAcct', OesInvAcctOverviewT),   # 深圳股东账户信息
        ('custName', c_char * OES_CUST_LONG_NAME_MAX_LEN),
                                                # 客户姓名
        ('__reserve', c_char * 64),             # 备用字段
    ]


class OesClientOverviewT(Structure):
    """
    客户端总览信息内容
    """
    _fields_ = [
        # 客户端名称
        ("clientName", c_char * OES_CLIENT_NAME_MAX_LEN),
        # 客户端说明
        ("clientMemo", c_char * OES_CLIENT_DESC_MAX_LEN),

        ("clientId", c_int16),                  # 客户端编号
        ("clientType", c_uint8),                # 客户端类型  @see eOesClientTypeT
        ("clientStatus", c_uint8),              # 客户端状态  @see eOesClientStatusT
        ("isApiForbidden", c_uint8),            # API禁用标识
        ("isBlockTrader", c_uint8),             # 是否大宗交易标识 @deprecated 已废弃
        ("businessScope", c_uint8),             # 服务端支持的业务范围 @see eOesBusinessTypeT
        ("currentBusinessType", c_uint8),       # 当前会话对应的业务类型 @see eOesBusinessTypeT
        ("logonTime", c_int64),                 # 客户端登录(委托接收服务)时间

        ("sseStkPbuId", c_int32),               # 上海现货/信用账户对应的PBU代码
        ("sseOptPbuId", c_int32),               # 上海衍生品账户对应的PBU代码
        ("sseQualificationClass", c_uint8),     # 上海股东账户的投资者适当性管理分类 @see eOesQualificationClassT
        ("__filler2", c_uint8 * 7),             # 按64位对齐的填充域

        ("szseStkPbuId", c_int32),              # 深圳现货/信用账户对应的PBU代码
        ("szseOptPbuId", c_int32),              # 深圳衍生品账户对应的PBU代码
        ("szseQualificationClass", c_uint8),    # 深圳股东账户的投资者适当性管理分类 @see eOesQualificationClassT
        ("__filler3", c_uint8 * 7),             # 按64位对齐的填充域

        ("currOrdConnected", c_int32),          # 当前已连接的委托通道数量
        ("currRptConnected", c_int32),          # 当前已连接的回报通道数量
        ("currQryConnected", c_int32),          # 当前已连接的查询通道数量
        ("maxOrdConnect", c_int32),             # 委托通道允许的最大同时连接数量
        ("maxRptConnect", c_int32),             # 回报通道允许的最大同时连接数量
        ("maxQryConnect", c_int32),             # 查询通道允许的最大同时连接数量

        ("ordTrafficLimit", c_int32),           # 委托通道的流量控制
        ("qryTrafficLimit", c_int32),           # 查询通道的流量控制
        ("maxOrdCount", c_int32),               # 最大委托笔数限制

        ("initialCashAssetRatio", c_uint8),     # 客户在本结点的初始资金资产占比(百分比)
        ("isSupportInternalAllot", c_uint8),    # 是否支持两地交易内部资金划拨
        ("isCheckStkConcentrate", c_uint8),     # 是否启用现货集中度控制
        ("isSupportBankFundTrsf", c_uint8),     # 是否支持与银行间银证转帐

        ("__reserve", c_char * 124),            # 备用字段

        ("associatedCustCnt", c_int32),         # 客户端关联的客户数量
        # 客户端关联的客户数量
        ("custItems", OesCustOverviewT * OES_MAX_CUST_PER_CLIENT),
    ]


class OesCounterCashItemT(Structure):
    """
    主柜资金信息内容
    """
    _fields_ = [
        # 资金账户代码
        ("cashAcctId", c_char * OES_CASH_ACCT_ID_MAX_LEN),
        # 客户代码
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        # 客户姓名
        ("custName", c_char * OES_CUST_NAME_MAX_LEN),
        # 银行代码
        ("bankId", c_char * OES_BANK_NO_MAX_LEN),

        ("cashType", c_uint8),                  # 资金账户类别 @see eOesAcctTypeT
        ("cashAcctStatus", c_uint8),            # 资金账户状态 @see eOesAcctStatusT
        ("currType", c_uint8),                  # 币种类型 @see eOesCurrTypeT
        ("isFundTrsfDisabled", c_uint8),        # 是否禁止出入金
        ("__filler", c_uint8 * 4),              # 按64位对齐的填充域

        # 主柜可用资金余额，单位精确到元后四位，即1元 = 10000
        ("counterAvailableBal", c_int64),
        # 主柜可取资金余额，单位精确到元后四位，即1元 = 10000
        ("counterDrawableBal", c_int64),
        # 主柜资金更新时间 (seconds since the Epoch)
        ("counterCashUpdateTime", c_int64),
        # 保留字段
        ("__reserve", c_char * 32),
    ]


class OesCustItemT(Structure):
    """
    客户信息内容

    __OES_CUST_BASE_INFO_PKT
    """
    _fields_ = [
        # 客户代码
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        ("custType", c_uint8),                  # 客户类型 @see eOesCustTypeT
        ("status", c_uint8),                    # 客户状态 (0:正常, 非0:不正常)
        ("riskLevel", c_uint8),                 # OES风险等级 @see eOesSecurityRiskLevelT
        ("originRiskLevel", c_uint8),           # 客户原始风险等级
        ("institutionFlag", c_uint8),           # 机构标志 (0:个人投资者, 1:机构投资者)
        ("investorClass", c_uint8),             # 投资者分类 @see eOesInvestorClassT
        ("optSettlementCnfmFlag", c_uint8),     # 期权账户结算单确认标志 (0:未确认, 1:已确认)
        ("__CUST_BASE_filler1", c_uint8),       # 按64位对齐的填充域
        ("branchId", c_int32),                  # 交易营业部代码
        ("__CUST_BASE_filler2", c_uint32),      # 按64位对齐的填充域
    ]


class _OesInvAcctItemTgwInfoT(Structure):
    """
    股东账户绑定的交易网关信息
    """
    _fields_ = [
        ("tgwGrpNo", c_uint8),                  # 绑定的交易网关组编号
        ("tgwItemCount", c_uint8),              # 网关组下的交易网关条目数量
        ("firstTgwItemNo", c_uint8),            # 网关组下第一个交易网关条目编号
        ("maxTgwItemNo", c_uint8),              # 网关组下最大的交易网关条目编号
    ]


class OesInvAcctItemT(Structure):
    """
    证券账户内容

    __OES_INV_ACCT_BASE_INFO_PKT
    _OesInvAcctItem
    """

    _fields_ = [
        # 股东账户代码
        ("invAcctId", c_char * OES_INV_ACCT_ID_MAX_LEN),
        ("mktId", c_uint8),                     # 市场 @see eOesMarketIdT
        ("acctType", c_uint8),                  # 账户类型 @see eOesAcctTypeT
        ("status", c_uint8),                    # 账户状态, 同步于主柜或者通过MON手动设置 @see eOesAcctStatusT
        ("ownerType", c_uint8),                 # 股东账户的所有者类型 @see eOesOwnerTypeT
        ("optInvLevel", c_uint8),               # 投资者期权等级 @see eOesOptInvLevelT
        ("isTradeDisabled", c_uint8),           # 是否禁止交易 (仅供API查询使用)
        ("__INV_ACCT_BASE_filler", c_uint8 * 2),# 按64位对齐的填充域

        ("limits", c_uint64),                   # 证券账户权限限制 @see eOesLimitT
        ("permissions", c_uint64),              # 股东权限/客户权限 @see eOesTradingPermissionT

        ("pbuId", c_int32),                     # 席位号
        ("stkPositionLimitRatio", c_int32),     # 个股持仓比例阀值 @deprecated 已废弃, 为了兼容旧版本而保留
        ("subscriptionQuota", c_int32),         # 主板权益 (新股认购限额)
        ("kcSubscriptionQuota", c_int32),       # 科创板权益 (新股认购限额)
        ("riskWarningSecurityBuyQtyLimit", c_int32),
                                                # 风险警示板证券单日买入数量限制
        # 预留的备用字段
        ("__INV_ACCT_BASE_reserve", c_char * 20),

        # 绑定的交易网关信息
        ("tgwInfo", _OesInvAcctItemTgwInfoT),
        # 绑定的上交所债券平台交易网关信息
        ("sseBtpTgwInfo", _OesInvAcctItemTgwInfoT),

        # 客户代码
        ('custId', c_char * OES_CUST_ID_MAX_LEN)
    ]


class OesQryCursorT(Structure):
    """
    查询定位的游标结构
    """
    _fields_ = [
        ('seqNo', c_int32),                     # 查询位置
        ('isEnd', c_int8),                      # 是否是当前最后一个包
        ('__filler', c_int8 * 3),               # 按64位对齐的填充域
        ('userInfo', c_int64),                  # 用户私有信息 (由客户端自定义填充, 并在应答数据中原样返回)
    ]


class OesQryOrdFilterT(Structure):
    """
    查询委托信息过滤条件
    """
    _fields_ = [
        # 客户代码, 可选项
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        # 证券账户代码, 可选项
        ("invAcctId", c_char * OES_INV_ACCT_ID_MAX_LEN),
        # 市场代码, 可选项。如无需此过滤条件请使用 OES_MKT_ID_UNDEFINE @see eOesMarketIdT
        ("mktId", c_uint8),
        # 是否仅查询未关闭委托 (包括未全部成交或撤销的委托)
        ("isUnclosedOnly", c_uint8),
        ("clEnvId", c_int8),                    # 客户端环境号
        ("securityType", c_uint8),              # 证券类别  @see eOesSecurityTypeT
        ("bsType", c_uint8),                    # 买卖类型  @see eOesBuySellTypeT
        ("subSecurityType", c_uint8),           # 证券子类别  @see eOesSubSecurityTypeT
        ("__filler", c_uint8 * 2),              # 按64位对齐的填充域
        ("clOrdId", c_int64),                   # 客户委托编号, 可选项
        ("clSeqNo", c_int64),                   # 客户委托流水号, 可选项

        # 查询委托的起始时间 (格式为 HHMMSSsss, 比如 141205000 表示 14:12:05.000)
        ("startTime", c_int32),
        # 查询委托的结束时间 (格式为 HHMMSSsss, 比如 141205000 表示 14:12:05.000)
        ("endTime", c_int32),
        # 用户私有信息 (由客户端自定义填充, 并在应答数据中原样返回)
        ("userInfo", c_int64),
    ]


class OesQryTrdFilterT(Structure):
    """
    查询成交信息过滤条件
    """
    _fields_ = [
        # 客户代码, 可选项
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        # 证券账户代码, 可选项
        ("invAcctId", c_char * OES_INV_ACCT_ID_MAX_LEN),
        # 市场代码, 可选项。如无需此过滤条件请使用 OES_MKT_ID_UNDEFINE @see eOesMarketIdT
        ("mktId", c_uint8),
        ("clEnvId", c_int8),                    # 客户端环境号
        ("securityType", c_uint8),              # 证券类别  @see eOesSecurityTypeT
        ("bsType", c_uint8),                    # 买卖类型  @see eOesBuySellTypeT
        ("subSecurityType", c_uint8),           # 证券子类别  @see eOesSubSecurityTypeT
        ("__filler", c_uint8 * 3),              # 按64位对齐的填充域
        ("clOrdId", c_int64),                   # 内部委托编号, 可选项
        ("clSeqNo", c_int64),                   # 客户委托流水号, 可选项
        ("startTime", c_int32),                 # 成交开始时间 (格式为 HHMMSSsss, 形如 141205000)
        ("endTime", c_int32),                   # 成交结束时间
        ("userInfo", c_int64),                  # 用户私有信息 (由客户端自定义填充, 并在应答数据中原样返回)
    ]


class OesQryCashAssetFilterT(Structure):
    """
    查询客户资金信息过滤条件
    """
    _fields_ = [
        # 客户代码, 可选项
        ('custId', c_char * OES_CUST_ID_MAX_LEN),
        # 资金账户代码, 可选项
        ('cashAcctId', c_char * OES_CASH_ACCT_ID_MAX_LEN),
        # 用户私有信息 (由客户端自定义填充, 并在应答数据中原样返回)
        ('userInfo', c_int64),
    ]


class OesQryStkHoldingFilterT(Structure):
    """
    查询股票持仓信息/信用持仓信息过滤条件
    """
    _fields_ = [
        # 客户代码, 可选项
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        # 证券账户代码, 可选项
        ("invAcctId", c_char * OES_INV_ACCT_ID_MAX_LEN),
        # 证券代码, 可选项
        ("securityId", c_char * OES_SECURITY_ID_MAX_LEN),
        ("mktId", c_uint8),                     # 市场代码  @see eOesMarketIdT
        ("securityType", c_uint8),              # 证券类别  @see eOesSecurityTypeT
        ("productType", c_uint8),               # 产品类型 @see eOesProductTypeT
        ("subSecurityType", c_uint8),           # 证券子类别  @see eOesSubSecurityTypeT
        ("__filler", c_uint8 * 4),              # 按64位对齐的填充域
        ("userInfo", c_int64),                  # 用户私有信息 (由客户端自定义填充, 并在应答数据中原样返回)
    ]


class OesQryLotWinningFilterT(Structure):
    """
    查询新股配号、中签信息过滤条件
    """
    _fields_ = [
        # 客户代码, 可选项
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        # 证券账户代码, 可选项
        ("invAcctId", c_char * OES_INV_ACCT_ID_MAX_LEN),
        # 市场代码, 可选项。如无需此过滤条件请使用 OES_MKT_ID_UNDEFINE @see eOesMarketIdT
        ("mktId", c_uint8),
        # 中签、配号记录类型, 可选项. 如无需此过滤条件请使用 eOesLotTypeT.OES_LOT_TYPE_UNDEFINE @see eOesLotTypeT
        ("lotType", c_uint8),
        # 按64位对齐的填充域
        ("__filler", c_uint8 * 6),
        # 查询起始日期 (格式为 YYYYMMDD)
        ("startDate", c_int32),
        # 查询结束日期 (格式为 YYYYMMDD)
        ("endDate", c_int32),
        # 用户私有信息 (由客户端自定义填充, 并在应答数据中原样返回)
        ("userInfo", c_int64),
    ]


class OesQryCustFilterT(Structure):
    """
    查询客户信息过滤条件
    """
    _fields_ = [
        # 客户代码, 可选项
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        # 用户私有信息 (由客户端自定义填充, 并在应答数据中原样返回)
        ("userInfo", c_int64),
    ]


class OesQryInvAcctFilterT(Structure):
    """
    查询证券账户信息过滤条件
    """
    _fields_ = [
        # 客户代码, 可选项
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        # 证券账户代码, 可选项
        ("invAcctId", c_char * OES_INV_ACCT_ID_MAX_LEN),
        # 市场代码, 可选项。如无需此过滤条件请使用 OES_MKT_ID_UNDEFINE @see eOesMarketIdT
        ("mktId", c_uint8),
        # 按64位对齐的填充域
        ("__filler", c_uint8 * 7),
        # 用户私有信息 (由客户端自定义填充, 并在应答数据中原样返回)
        ("userInfo", c_int64),
    ]


class OesQryCommissionRateFilterT(Structure):
    """
    查询客户佣金信息过滤条件
    """
    _fields_ = [
        # 客户代码, 可选项
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        # 市场代码, 可选项。如无需此过滤条件请使用 OES_MKT_ID_UNDEFINE @see eOesMarketIdT
        ("mktId", c_uint8),
        # 证券类别, 可选项。如无需此过滤条件请使用 OES_SECURITY_TYPE_UNDEFINE @see eOesSecurityTypeT
        ("securityType", c_uint8),
        # 买卖类型, 可选项。如无需此过滤条件请使用 OES_BS_TYPE_UNDEFINE @see eOesBuySellTypeT
        ("bsType", c_uint8),
        # 按64位对齐的填充域
        ("__filler", c_uint8 * 5),
        # 用户私有信息 (由客户端自定义填充, 并在应答数据中原样返回)
        ("userInfo", c_int64),
    ]


class OesQryFundTransferSerialFilterT(Structure):
    """
    查询出入金流水信息过滤条件
    """
    _fields_ = [
        # 客户代码, 可选项
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        # 资金账户代码, 可选项
        ("cashAcctId", c_char * OES_CASH_ACCT_ID_MAX_LEN),
        # 出入金流水号, 可选项
        ("clSeqNo", c_int32),
        # 客户端环境号
        ("clEnvId", c_int8),
        # 按64位对齐的填充域
        ("__filler", c_uint8 * 3),
        # 用户私有信息 (由客户端自定义填充, 并在应答数据中原样返回)
        ("userInfo", c_int64),
    ]


class OesQryIssueFilterT(Structure):
    """
    查询证券发行信息过滤条件
    """
    _fields_ = [
        # 证券发行代码, 可选项
        ("securityId", c_char * OES_SECURITY_ID_MAX_LEN),
        # 市场代码, 可选项。如无需此过滤条件请使用 OES_MKT_UNDEFINE @see eOesMarketIdT
        ("mktId", c_uint8),
        # 产品类型, 默认将仅查询新股发行信息, 即产品类型默认为 OES_PRODUCT_TYPE_IPO
        # 如需查询配股发行信息, 需指定产品类型为 OES_PRODUCT_TYPE_ALLOTMENT @see eOesProductTypeT
        ("productType", c_uint8),
        # 按64位对齐的填充域
        ("__filler", c_uint8 * 6),
        # 用户私有信息 (由客户端自定义填充, 并在应答数据中原样返回)
        ("userInfo", c_int64),
    ]


class OesQryStockFilterT(Structure):
    """
    查询证券信息(现货产品信息)过滤条件
    """
    _fields_ = [
        # 证券代码, 可选项
        ("securityId", c_char * OES_SECURITY_ID_MAX_LEN),
        # 市场代码, 可选项。如无需此过滤条件请使用 OES_MKT_ID_UNDEFINE @see eOesMarketIdT
        ("mktId", c_uint8),
        # 证券类别  @see eOesSecurityTypeT
        ("securityType", c_uint8),
        # 证券子类别  @see eOesSubSecurityTypeT
        ("subSecurityType", c_uint8),
        # 融资融券担保品标识 (0:未指定, 1:是担保品, 2:不是担保品)
        ("crdCollateralFlag", c_int8),
        # 融资标的标识 (0:未指定, 1:是融资标的, 2:不是融资标的)
        ("crdMarginTradeUnderlyingFlag", c_int8),
        # 融券标的标识 (0:未指定, 1:是融券标的, 2:不是融券标的
        ("crdShortSellUnderlyingFlag", c_int8),
        # 按64位对齐的填充域
        ("__filler", c_uint8 * 2),
        # 用户私有信息 (由客户端自定义填充, 并在应答数据中原样返回)
        ("userInfo", c_int64),
    ]


class OesQryEtfFilterT(Structure):
    """
    查询ETF申赎产品信息过滤条件
    """
    _fields_ = [
        # ETF基金申赎代码, 可选项
        ("fundId", c_char * OES_SECURITY_ID_MAX_LEN),
        # ETF基金市场代码, 可选项。如无需此过滤条件请使用 OES_MKT_ID_UNDEFINE @see eOesMarketIdT
        ("mktId", c_uint8),
        # 按64位对齐的填充域
        ("__filler", c_uint8 * 7),
        # 用户私有信息 (由客户端自定义填充, 并在应答数据中原样返回)
        ("userInfo", c_int64),
    ]


class OesQryEtfComponentFilterT(Structure):
    """
    查询ETF成份证券信息过滤条件
    """
    _fields_ = [
        # ETF基金申赎代码
        ("fundId", c_char * OES_SECURITY_ID_MAX_LEN),
        # ETF基金市场代码 (可选项, 如无需此过滤条件请使用 OES_MKT_ID_UNDEFINE) @see eOesMarketIdT
        ("fundMktId", c_uint8),
        # 按64位对齐的填充域
        ("__filler", c_uint8 * 7),
        # 用户私有信息 (由客户端自定义填充, 并在应答数据中原样返回)
        ("userInfo", c_int64),
    ]


class OesQryMarketStateFilterT(Structure):
    """
    查询市场状态信息过滤条件
    """
    _fields_ = [
        # 交易所代码 (可选项, 为 0 则匹配所有交易所) @see eOesExchangeIdT
        ("exchId", c_uint8),
        # 交易平台代码 (可选项, 为 0 则匹配所有交易平台) @see eOesPlatformIdT
        ("platformId", c_uint8),
        # 按64位对齐的填充域
        ("__filler", c_uint8 * 6),
        # 用户私有信息 (由客户端自定义填充, 并在应答数据中原样返回)
        ("userInfo", c_int64),
    ]


class OesQryNotifyInfoFilterT(Structure):
    """
    查询通知消息过滤条件
    """
    _fields_ = [
        # 客户代码, 可选项
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        # 通知消息等级 @see eOesNotifyLevelT
        ("notifyLevel", c_uint8),
        # 按64位对齐的填充域
        ("__filler", c_uint8 * 7),
        # 用户私有信息 (由客户端自定义填充, 并在应答数据中原样返回)
        ("userInfo", c_int64),
    ]


class _OesBrokerParamsCreditExtInfoT(Structure):
    """
    券商参数信息两融业务的扩展信息
    """
    _fields_ = [
        ("singleMarginBuyCeiling", c_int64),    # 单笔融资买入委托金额上限
        ("singleShortSellCeiling", c_int64),    # 单笔融券卖出委托金额上限
        ("safetyLineRatio", c_int32),           # 维持担保比安全线 (千分比)
        ("withdrawLineRatio", c_int32),         # 维持担保比提取线 (千分比)
        ("warningLineRatio", c_int32),          # 维持担保比警戒线 (千分比)
        ("liqudationLineRatio", c_int32),       # 维持担保比平仓线 (千分比)
        ("isRepayInterestOnlyAble", c_uint8),   # 是否支持使用 '仅归还息费' 模式归还融资融券负债的息费
        ("__filler", c_uint8 * 7)               # 按64位对齐的填充域
    ]


class _OesBrokerParamsOptionExtInfoT(Structure):
    """
    券商参数信息期权业务的扩展信息
    """
    _fields_ = [
        ("withdrawLineRatio", c_int32),         # 出金提取线 (万分比)
        ("marginCallLineRatio", c_int32),       # 保证金盘中追保线 (万分比)
        ("liqudationLineRatio", c_int32),       # 保证金盘中平仓线 (万分比)
        ("marginDisposalLineRatio", c_int32),   # 保证金即时处置线 (万分比)
    ]


class _UnionForOesBrokerParamsExtInfoT(Union):
    _fields_ = [
        ('creditExt', _OesBrokerParamsCreditExtInfoT),
        ('optionExt', _OesBrokerParamsOptionExtInfoT),
        ('__extInfo', c_char * 192)
    ]


class OesBrokerParamsInfoT(Structure):
    """
    券商参数信息
    """
    _fields_ = [
        # 券商名称
        ("brokerName", c_char * OES_BROKER_NAME_MAX_LEN),
        # 券商电话
        ("brokerPhone", c_char * OES_BROKER_PHONE_MAX_LEN),
        # 券商网址
        ("brokerWebsite", c_char * OES_BROKER_WEBSITE_MAX_LEN),
        # 当前版本号
        ("apiVersion", c_char * OES_VER_ID_MAX_LEN),
        # 为兼容协议而添加的填充域
        ("__filler1", c_char * 8),

        # API兼容的最低协议版本号
        ("apiMinVersion", c_char * OES_VER_ID_MAX_LEN),
        # 为兼容协议而添加的填充域
        ("__filler2", c_char * 8),

        # 客户端最新版本号
        ("clientVersion", c_char * OES_VER_ID_MAX_LEN),
        # 为兼容协议而添加的填充域
        ("__filler3", c_char * 8),

        # 限制客户端修改密码的结束时间 (HHMMSSsss)
        ("forbidChangePwdEndTime", c_int32),
        # 客户端密码允许的最小长度
        ("minClientPasswordLen", c_int32),
        # 客户端密码强度级别
        ("clientPasswordStrength", c_int32),
        # 服务端支持的业务范围 @see eOesBusinessTypeT
        ("businessScope", c_uint32),
        # 当前会话对应的业务类型 @see eOesBusinessTypeT
        ("currentBusinessType", c_uint8),
        # 服务端是否支持两地交易内部资金划拨
        ("isSupportInternalAllot", c_uint8),
        # 服务端是否支持与银行间银证转帐
        ("isSupportBankFundTrsf", c_uint8),
        # 按64位对齐的填充域
        ("__filler4", c_uint8),

        # 限制客户端修改密码的开始时间 (HHMMSSsss)
        ("forbidChangePwdBeginTime", c_int32),
        # 客户代码
        ("custId", c_char * OES_CUST_ID_MAX_LEN),
        # 上证风险警示板证券单日买入数量限制
        ("sseRiskWarningSecurityBuyQtyLimit", c_int64),
        # 深证风险警示板证券单日买入数量限制
        ("szseRiskWarningSecurityBuyQtyLimit", c_int64),
        # 预留的备用字段
        ("__reserve", c_char * 24),
        # 业务范围扩展信息
        ("_union0", _UnionForOesBrokerParamsExtInfoT)
    ]
