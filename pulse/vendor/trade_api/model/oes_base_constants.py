# -*- coding: utf-8 -*-
"""常量相关"""

try:
    from .spk_util import (
        SPK_MAX_PATH_LEN, STimespec32T, UnionForUserInfo
    )
except ImportError:
    from sutil.spk_util import (
        SPK_MAX_PATH_LEN, STimespec32T, UnionForUserInfo
    )


# ===================================================================
# 常量定义 (宏定义)
# ===================================================================

# 密码最大长度
OES_PWD_MAX_LEN                                 = 40
# 银行代码最大长度
OES_BANK_NO_MAX_LEN                             = 8
# 客户代码最大长度
OES_CUST_ID_MAX_LEN                             = 16
# 客户名称最大长度
OES_CUST_NAME_MAX_LEN                           = 64
# 错误描述信息长度
OES_MAX_ERROR_INFO_LEN                          = 64
# 客户端对应的最大客户数量
OES_MAX_CUST_PER_CLIENT                         = 1
# 测试请求标识符的最大长度
OES_MAX_TEST_REQ_ID_LEN                         = 32
# 股东账户代码最大长度
OES_INV_ACCT_ID_MAX_LEN                         = 16
# 发送时间字段(YYYYMMDD-HH:mm:SS.sss (*C21))的最大长度
OES_MAX_SENDING_TIME_LEN                        = 22
# 股东账户代码最大长度
OES_SECURITY_ID_MAX_LEN                         = 16
# 客户端名称最大长度
OES_CLIENT_NAME_MAX_LEN                         = 32
# 客户端说明最大长度
OES_CLIENT_DESC_MAX_LEN                         = 32
# 客户端标签最大长度
OES_CLIENT_TAG_MAX_LEN                          = 32
# 资金账户代码最大长度
OES_CASH_ACCT_ID_MAX_LEN                        = 16
# 交易所订单编号的最大长度
OES_EXCH_ORDER_ID_MAX_LEN                       = 17
# 证券名称长度
OES_SECURITY_NAME_MAX_LEN                       = 24
# 融资融券合约编号最大长度
OES_CREDIT_DEBT_ID_MAX_LEN                      = 32
# 主柜调拨流水号信息长度
OES_MAX_ALLOT_SERIALNO_LEN                      = 64
# 消息通知内容的最大长度
OES_NOTIFY_CONTENT_MAX_LEN                      = 296
# 客户长名称最大长度
OES_CUST_LONG_NAME_MAX_LEN                      = 128
# 期权合约代码简称长度
OES_CONTRACT_SYMBOL_MAX_LEN                     = 56
# 期权合约交易代码长度
OES_CONTRACT_EXCH_ID_MAX_LEN                    = 24
# 期权合约状态信息长度
OES_SECURITY_STATUS_FLAG_MAX_LEN                = 8

# 券商名称最大长度
OES_BROKER_NAME_MAX_LEN                         = 128
# 券商电话最大长度
OES_BROKER_PHONE_MAX_LEN                        = 32
# 券商网址最大长度
OES_BROKER_WEBSITE_MAX_LEN                      = 256
# OES版本号最大长度
OES_VER_ID_MAX_LEN                              = 32
# -------------------------



class eOesExchangeIdT:
    """
    交易所代码定义
    """
    OES_EXCH_UNDEFINE                   = 0  # 未定义的交易所代码
    OES_EXCH_SSE                        = 1  # 上海证券交易所
    OES_EXCH_SZSE                       = 2  # 深圳证券交易所


class eOesMarketIdT:
    """
    市场类型定义
    """
    OES_MKT_UNDEFINE                    = 0  # 未定义的市场类型
    OES_MKT_SH_ASHARE                   = 1  # 上海A股
    OES_MKT_SZ_ASHARE                   = 2  # 深圳A股
    OES_MKT_SH_OPTION                   = 3  # 上海期权
    OES_MKT_SZ_OPTION                   = 4  # 深圳期权

    # 扩展的其他市场定义 (仅用于查询)
    OES_MKT_EXT_HK                      = 11  # 港交所股票, 仅用于跨沪深港ETF的成分股
    OES_MKT_EXT_BJ                      = 12  # 北交所股票, 仅用于跨沪深京港ETF的成分股
    OES_MKT_EXT_OTHER                   = 99  # 其他市场, 仅用于ETF成分股


class eOesOrdTypeT:
    """
    委托类型
    部分缩写解释如下:
    - LMT (Limit)           : 限价
    - MTL (Market To Limit) : 剩余转限价(市价)
    - FAK (Fill and Kill)   : 剩余转撤销(市价)
    - FOK (Fill or Kill)    : 全部成交或全部撤销(市价/限价)

    上海A股支持类型:
    1. OES_ORD_TYPE_LMT
    2. OES_ORD_TYPE_MTL_BEST_5
    3. OES_ORD_TYPE_FAK_BEST_5
    4. OES_ORD_TYPE_MTL_BEST (仅适用于科创板)
    5. OES_ORD_TYPE_MTL_SAMEPARTY_BEST (仅适用于科创板)

    上海期权支持市价类型:
    1. OES_ORD_TYPE_LMT
    2. OES_ORD_TYPE_LMT_FOK
    3. OES_ORD_TYPE_MTL
    4. OES_ORD_TYPE_FAK
    5. OES_ORD_TYPE_FOK

    深圳A股支持市价类型:
    1. OES_ORD_TYPE_LMT
    2. OES_ORD_TYPE_MTL_BEST
    3. OES_ORD_TYPE_MTL_SAMEPARTY_BEST
    4. OES_ORD_TYPE_FAK_BEST_5
    5. OES_ORD_TYPE_FAK
    6. OES_ORD_TYPE_FOK

    深圳期权支持市价类型:
    1. OES_ORD_TYPE_LMT
    2. OES_ORD_TYPE_LMT_FOK
    3. OES_ORD_TYPE_MTL_BEST
    4. OES_ORD_TYPE_MTL_SAMEPARTY_BEST
    5. OES_ORD_TYPE_FAK_BEST_5
    6. OES_ORD_TYPE_FAK
    7. OES_ORD_TYPE_FOK
    """

    OES_ORD_TYPE_LMT                    = 0   # 限价委托
    OES_ORD_TYPE_LMT_FOK                = 1   # 限价全部成交或全部撤销委托
    OES_ORD_TYPE_MTL_BEST_5             = 10  # 最优五档即时成交剩余转限价委托
    OES_ORD_TYPE_MTL_BEST               = 11  # 对手方最优价格委托
    OES_ORD_TYPE_MTL_SAMEPARTY_BEST     = 12  # 本方最优价格委托
    OES_ORD_TYPE_MTL                    = 13  # 市价剩余转限价委托
    OES_ORD_TYPE_FAK_BEST_5             = 20  # 最优五档即时成交剩余撤销委托
    OES_ORD_TYPE_FAK                    = 21  # 即时成交剩余撤销委托
    OES_ORD_TYPE_FOK                    = 30  # 市价全部成交或全部撤销委托


class eOesOrdTypeShT:
    """
    上证委托类型

    部分缩写解释如下:
    - LMT (Limit)           : 限价
    - MTL (Market To Limit) : 剩余转限价(市价)
    - FAK (Fill and Kill)   : 剩余转撤销(市价)
    - FOK (Fill or Kill)    : 全部成交或全部撤销(市价/限价)
    """
    # 限价, 0
    OES_ORD_TYPE_SH_LMT                 = eOesOrdTypeT.OES_ORD_TYPE_LMT

    # 最优五档即时成交剩余转限价委托, 10
    OES_ORD_TYPE_SH_MTL_BEST_5          = eOesOrdTypeT.OES_ORD_TYPE_MTL_BEST_5
    # 对手方最优价格委托(仅适用于科创板), 11
    OES_ORD_TYPE_SH_MTL_BEST            = eOesOrdTypeT.OES_ORD_TYPE_MTL_BEST
    # 本方最优价格委托(仅适用于科创板), 12
    OES_ORD_TYPE_SH_MTL_SAMEPARTY_BEST  = eOesOrdTypeT.OES_ORD_TYPE_MTL_SAMEPARTY_BEST
    # 最优五档即时成交剩余撤销委托, 20
    OES_ORD_TYPE_SH_FAK_BEST_5          = eOesOrdTypeT.OES_ORD_TYPE_FAK_BEST_5


class eOesOrdTypeShOptT:
    """
    上证期权业务委托类型

    部分缩写解释如下:
    - LMT (Limit)           : 限价
    - MTL (Market To Limit) : 剩余转限价(市价)
    - FAK (Fill and Kill)   : 剩余转撤销(市价)
    - FOK (Fill or Kill)    : 全部成交或全部撤销(市价/限价)
    """
    # 限价, 0
    OES_ORD_TYPE_SHOPT_LMT              = eOesOrdTypeT.OES_ORD_TYPE_LMT
    # 限价全部成交或全部撤销委托, 1
    OES_ORD_TYPE_SHOPT_LMT_FOK          = eOesOrdTypeT.OES_ORD_TYPE_LMT_FOK

    # 市价剩余转限价委托, 13
    OES_ORD_TYPE_SHOPT_MTL              = eOesOrdTypeT.OES_ORD_TYPE_MTL
    # 即时成交剩余撤销委托, 21
    OES_ORD_TYPE_SHOPT_FAK              = eOesOrdTypeT.OES_ORD_TYPE_FAK
    # 市价全部成交或全部撤销委托, 30
    OES_ORD_TYPE_SHOPT_FOK              = eOesOrdTypeT.OES_ORD_TYPE_FOK


class eOesOrdTypeSzT:
    """
    深证委托类型

    部分缩写解释如下:
    - LMT (Limit)           : 限价
    - MTL (Market To Limit) : 剩余转限价(市价)
    - FAK (Fill and Kill)   : 剩余转撤销(市价)
    - FOK (Fill or Kill)    : 全部成交或全部撤销(市价/限价)
    """
    # 限价, 0
    OES_ORD_TYPE_SZ_LMT                 = eOesOrdTypeT.OES_ORD_TYPE_LMT
    # 限价全部成交或全部撤销委托(仅适用于期权), 1
    OES_ORD_TYPE_SZ_LMT_FOK             = eOesOrdTypeT.OES_ORD_TYPE_LMT_FOK

    # 对手方最优价格委托, 11
    OES_ORD_TYPE_SZ_MTL_BEST            = eOesOrdTypeT.OES_ORD_TYPE_MTL_BEST
    # 本方最优价格委托, 12
    OES_ORD_TYPE_SZ_MTL_SAMEPARTY_BEST  = eOesOrdTypeT.OES_ORD_TYPE_MTL_SAMEPARTY_BEST
    # 最优五档即时成交剩余撤销委托, 20
    OES_ORD_TYPE_SZ_FAK_BEST_5          = eOesOrdTypeT.OES_ORD_TYPE_FAK_BEST_5
    # 即时成交剩余撤销委托, 21
    OES_ORD_TYPE_SZ_FAK                 = eOesOrdTypeT.OES_ORD_TYPE_FAK
    # 市价全部成交或全部撤销委托, 30
    OES_ORD_TYPE_SZ_FOK                 = eOesOrdTypeT.OES_ORD_TYPE_FOK


class eOesBuySellTypeT:
    """
    买卖类型
    """
    OES_BS_TYPE_UNDEFINE                = 0  # 未定义的买卖类型
    OES_BS_TYPE_BUY                     = 1  # 普通买入/信用担保品买入
    OES_BS_TYPE_SELL                    = 2  # 普通卖出/信用担保品卖出
    OES_BS_TYPE_CREATION                = 3  # 申购
    OES_BS_TYPE_REDEMPTION              = 4  # 赎回
    OES_BS_TYPE_REVERSE_REPO            = 6  # 质押式逆回购
    OES_BS_TYPE_SUBSCRIPTION            = 7  # 新股/可转债/可交换债认购
    OES_BS_TYPE_ALLOTMENT               = 8  # 配股/配债认购
    # -------------------------

    OES_BS_TYPE_BUY_OPEN                = 11  # 期权买入开仓
    OES_BS_TYPE_SELL_CLOSE              = 12  # 期权卖出平仓
    OES_BS_TYPE_SELL_OPEN               = 13  # 期权卖出开仓
    OES_BS_TYPE_BUY_CLOSE               = 14  # 期权买入平仓
    OES_BS_TYPE_COVERED_OPEN            = 15  # 期权备兑开仓
    OES_BS_TYPE_COVERED_CLOSE           = 16  # 期权备兑平仓
    OES_BS_TYPE_OPTION_EXERCISE         = 17  # 期权行权
    OES_BS_TYPE_UNDERLYING_FREEZE       = 18  # 期权标的锁定
    OES_BS_TYPE_UNDERLYING_UNFREEZE     = 19  # 期权标的解锁
    # -------------------------

    OES_BS_TYPE_CANCEL                  = 30  # 撤单
    # -------------------------

    # 信用担保品买入
    OES_BS_TYPE_COLLATERAL_BUY          = OES_BS_TYPE_BUY
    # 信用担保品卖出
    OES_BS_TYPE_COLLATERAL_SELL         = OES_BS_TYPE_SELL
    OES_BS_TYPE_COLLATERAL_TRANSFER_IN  = 31  # 信用担保品转入
    OES_BS_TYPE_COLLATERAL_TRANSFER_OUT = 32  # 信用担保品转出
    OES_BS_TYPE_MARGIN_BUY              = 33  # 信用融资买入
    OES_BS_TYPE_REPAY_MARGIN_BY_SELL    = 34  # 信用卖券还款
    OES_BS_TYPE_SHORT_SELL              = 35  # 信用融券卖出
    OES_BS_TYPE_REPAY_STOCK_BY_BUY      = 36  # 信用买券还券
    OES_BS_TYPE_REPAY_STOCK_DIRECT      = 37  # 信用直接还券
    # -------------------------

    # 仅用于兼容之前版本的质押式逆回购 不可用于‘信用融券卖出’交易
    OES_BS_TYPE_CREDIT_SELL             = OES_BS_TYPE_REVERSE_REPO
    OES_BS_TYPE_B                       = OES_BS_TYPE_BUY
    OES_BS_TYPE_S                       = OES_BS_TYPE_SELL
    OES_BS_TYPE_KB                      = OES_BS_TYPE_CREATION
    OES_BS_TYPE_KS                      = OES_BS_TYPE_REDEMPTION
    OES_BS_TYPE_CS                      = OES_BS_TYPE_REVERSE_REPO
    OES_BS_TYPE_BO                      = OES_BS_TYPE_BUY_OPEN
    OES_BS_TYPE_BC                      = OES_BS_TYPE_BUY_CLOSE
    OES_BS_TYPE_SO                      = OES_BS_TYPE_SELL_OPEN
    OES_BS_TYPE_SC                      = OES_BS_TYPE_SELL_CLOSE
    OES_BS_TYPE_CO                      = OES_BS_TYPE_COVERED_OPEN
    OES_BS_TYPE_CC                      = OES_BS_TYPE_COVERED_CLOSE
    OES_BS_TYPE_TE                      = OES_BS_TYPE_OPTION_EXERCISE
    OES_BS_TYPE_UF                      = OES_BS_TYPE_UNDERLYING_FREEZE
    OES_BS_TYPE_UU                      = OES_BS_TYPE_UNDERLYING_UNFREEZE


class eOesPlatformIdT:
    """
    交易平台类型定义
    """
    OES_PLATFORM_UNDEFINE               = 0  # 未定义的交易平台类型
    OES_PLATFORM_CASH_AUCTION           = 1  # 现货集中竞价交易平台
    OES_PLATFORM_FINANCIAL_SERVICES     = 2  # 综合金融服务平台
    OES_PLATFORM_NON_TRADE              = 3  # 非交易处理平台
    OES_PLATFORM_DERIVATIVE_AUCTION     = 4  # 衍生品集中竞价交易平台
    OES_PLATFORM_INTERNATIONAL_MARKET   = 5  # 国际市场互联平台 (暂未对接)
    OES_PLATFORM_BOND_TRADING           = 6  # 新债券交易平台


class eOesTrdCnfmTypeT:
    """
    成交回报记录的成交类型
    上证接口规范 (IS103_ETFInterface_CV14_20130123) 中规定如下:
    - 二级市场记录表示一笔申购/赎回交易连续记录的开始,对一笔申购/赎回交易而言,有且只有一条;
    - 一级市场记录不再表示对应申购/赎回交易连续记录的结束,对一笔申购/赎回交易而言,有且只有一条。
    上证综合业务平台接口规格说明书 (IS105_ATPInterface_CV1.49_ETF_Test_20210906) 中描述如下:
    - ETF实物申购/赎回时, 可能会不存在资金替代执行报告
    上证期权接口规格说明书 (IS113_DTPInterface_CV1.1_20161017) 中描述如下:
    - 执行报告中的会员内部编号(clOrdId)以QP1开头，表示为交易所保证金强制平仓
    - 执行报告中的会员内部编号(clOrdId)以CV1开头，表示为交易所备兑强制平仓
    """
    OES_TRDCNFM_TYPE_NORMAL             = 0  # 普通成交记录

    OES_TRDCNFM_TYPE_ETF_FIRST          = 1  # ETF 二级市场记录
    OES_TRDCNFM_TYPE_ETF_CMPOENT        = 2  # ETF 成份股记录
    OES_TRDCNFM_TYPE_ETF_CASH           = 3  # ETF 资金记录
    OES_TRDCNFM_TYPE_ETF_LAST           = 4  # ETF 一级市场记录

    OES_TRDCNFM_TYPE_OPT_QP1            = 11  # OPT 交易所保证金强制平仓
    OES_TRDCNFM_TYPE_OPT_CV1            = 12  # OPT 交易所备兑强制平仓


class eOesFundTrsfDirectT:
    """
    出入金方向定义
    """
    OES_FUND_TRSF_DIRECT_IN             = 0  # 转入OES (入金)
    OES_FUND_TRSF_DIRECT_OUT            = 1  # 转出OES (出金)


class eOesFundTrsfTypeT:
    """
    出入金转账类型定义
    """
    OES_FUND_TRSF_TYPE_OES_BANK         = 0  # OES和银行之间转账
    OES_FUND_TRSF_TYPE_OES_COUNTER      = 1  # OES和主柜之间划拨资金
    OES_FUND_TRSF_TYPE_COUNTER_BANK     = 2  # 主柜和银行之间转账
    OES_FUND_TRSF_TYPE_OES_TO_OES       = 3  # 沪深OES之间的内部资金划拨


class eOesFundTrsfStatusT:
    """
    出入金委托状态
    """
    OES_FUND_TRSF_STS_UNDECLARED        = 0  # 尚未上报
    OES_FUND_TRSF_STS_DECLARED          = 1  # 已上报
    OES_FUND_TRSF_STS_WAIT_DONE         = 2  # 主柜处理完成 等待事务结束
    OES_FUND_TRSF_STS_DONE              = 3  # 出入金处理完成
    OES_FUND_TRSF_STS_ROLLBACK_MIN      = 5  # 出入金失败判断标志
    OES_FUND_TRSF_STS_UNDECLARED_ROLLBACK \
                                        = 6  # 待回滚(未上报前)
    OES_FUND_TRSF_STS_DECLARED_ROLLBACK = 7  # 待回滚(已上报后)
    OES_FUND_TRSF_STS_INVALID_MIN       = 10  # 出入金废单判断标志
    OES_FUND_TRSF_STS_INVALID_OES       = 11  # OES内部判断为废单
    OES_FUND_TRSF_STS_INVALID_COUNTER   = 12  # 主柜判断为废单
    OES_FUND_TRSF_STS_SUSPENDED         = 13  # 挂起状态 (主柜的出入金执行状态未知 待人工干预处理)


class eOesFundTrsfSourceTypeT:
    """
    出入金指令来源分类
    """
    OES_FUND_TRSF_SOURCE_UNDEFINE       = 0  # 未定义
    OES_FUND_TRSF_SOURCE_CUST           = 1  # 客户发起
    OES_FUND_TRSF_SOURCE_TIMER          = 2  # 系统内部定时任务发起
    OES_FUND_TRSF_SOURCE_COLO_PEER      = 3  # 两地交易的对端结点发起
    OES_FUND_TRSF_SOURCE_MON            = 4  # MON管理端发起


class eOesCrdAssignableRepayModeT:
    """
    可以由API接口指定的融资融券负债归还模式
    """
    OES_CRD_ASSIGNABLE_REPAY_MODE_DEFAULT \
                                        = 0  # 默认的负债归还模式 (使用融资融券合同约定的负债归还模式)
    OES_CRD_ASSIGNABLE_REPAY_MODE_INTEREST_ONLY \
                                        = 10  # 仅归还息费


class eOesBusinessTypeT:
    """
    业务类型定义
    """
    OES_BUSINESS_TYPE_UNDEFINE          = 0x0  # 未定义的业务类型
    OES_BUSINESS_TYPE_STOCK             = 0x01  # 现货业务
    OES_BUSINESS_TYPE_OPTION            = 0x02  # 期权业务
    OES_BUSINESS_TYPE_CREDIT            = 0x04  # 信用业务
    OES_BUSINESS_TYPE_ALL               = 0xFF  # 所有业务


class eOesTrdSessTypeT:
    """
    OES 竞价时段定义
    """
    OES_TRD_SESS_TYPE_O                 = 0  # 开盘集合竞价时段
    OES_TRD_SESS_TYPE_T                 = 1  # 连续竞价时段
    OES_TRD_SESS_TYPE_C                 = 2  # 收盘集合竞价


class eOesSecurityTypeT:
    """
    证券类别
    """
    OES_SECURITY_TYPE_UNDEFINE          = 0  # 未定义的证券类型
    OES_SECURITY_TYPE_STOCK             = 1  # 股票
    OES_SECURITY_TYPE_BOND              = 2  # 债券
    OES_SECURITY_TYPE_ETF               = 3  # ETF
    OES_SECURITY_TYPE_FUND              = 4  # 基金
    OES_SECURITY_TYPE_OPTION            = 5  # 期权
    OES_SECURITY_TYPE_MGR               = 9  # 管理类


class eOesSubSecurityTypeT:
    """
    证券子类别
    """
    OES_SUB_SECURITY_TYPE_UNDEFINE      = 0  # 未定义的证券子类型

    OES_SUB_SECURITY_TYPE_STOCK_MIN     = 10  # 股票类证券子类型最小值
    OES_SUB_SECURITY_TYPE_STOCK_ASH     = 11  # A股股票, A Share
    OES_SUB_SECURITY_TYPE_STOCK_SME     = 12  # 中小板股票, Small & Medium Enterprise (SME) Board
    OES_SUB_SECURITY_TYPE_STOCK_GEM     = 13  # 创业板股票, Growth Enterprise Market (GEM)
    OES_SUB_SECURITY_TYPE_STOCK_KSH     = 14  # 科创板股票
    OES_SUB_SECURITY_TYPE_STOCK_KCDR    = 15  # 科创板存托凭证
    OES_SUB_SECURITY_TYPE_STOCK_CDR     = 16  # 存托凭证, Chinese Depository Receipt (CDR)
    OES_SUB_SECURITY_TYPE_STOCK_HLTCDR  = 17  # 沪伦通CDR本地交易业务产品
    OES_SUB_SECURITY_TYPE_STOCK_GEMCDR  = 18  # 创业板存托凭证
    OES_SUB_SECURITY_TYPE_STOCK_MAX     = 19  # 股票类证券子类型最大值

    OES_SUB_SECURITY_TYPE_BOND_MIN      = 20  # 债券类证券子类型最小值
    OES_SUB_SECURITY_TYPE_BOND_GBF      = 21  # 国债 (国债/地方债/政策性金融债/上交所政府支持债)
    OES_SUB_SECURITY_TYPE_BOND_CBF      = 22  # 企业债
    OES_SUB_SECURITY_TYPE_BOND_CPF      = 23  # 公司债
    OES_SUB_SECURITY_TYPE_BOND_CCF      = 24  # 可转换债券
    OES_SUB_SECURITY_TYPE_BOND_FBF      = 25  # 金融机构发行债券 (仅适用于深交所, 上交所已废弃)
    OES_SUB_SECURITY_TYPE_BOND_PRP      = 26  # 通用质押式回购
    OES_SUB_SECURITY_TYPE_BOND_STD      = 27  # 债券标准券
    OES_SUB_SECURITY_TYPE_BOND_EXG      = 28  # 可交换债券
    OES_SUB_SECURITY_TYPE_BOND_MAX      = 29  # 债券类证券子类型最大值

    OES_SUB_SECURITY_TYPE_ETF_MIN       = 30  # ETF类证券子类型最小值
    OES_SUB_SECURITY_TYPE_ETF_SINGLE_MKT \
                                        = 31  # 单市场股票ETF
    OES_SUB_SECURITY_TYPE_ETF_CROSS_MKT = 32  # 跨市场股票ETF
    OES_SUB_SECURITY_TYPE_ETF_BOND      = 33  # 债券ETF(包括实物债券ETF和现金债券ETF)
    OES_SUB_SECURITY_TYPE_ETF_CURRENCY  = 34  # 货币ETF
    OES_SUB_SECURITY_TYPE_ETF_CROSS_BORDER \
                                        = 35  # 跨境ETF
    OES_SUB_SECURITY_TYPE_ETF_GOLD      = 36  # 黄金ETF
    OES_SUB_SECURITY_TYPE_ETF_COMMODITY_FUTURES \
                                        = 37  # 商品期货ETF
    OES_SUB_SECURITY_TYPE_ETF_MAX       = 38  # ETF类证券子类型最大值

    OES_SUB_SECURITY_TYPE_FUND_MIN      = 40  # 基金类证券子类型最小值
    OES_SUB_SECURITY_TYPE_FUND_LOF      = 41  # LOF基金
    OES_SUB_SECURITY_TYPE_FUND_CEF      = 42  # 封闭式基金, Close-end Fund
    OES_SUB_SECURITY_TYPE_FUND_OEF      = 43  # 开放式基金, Open-end Fund
    OES_SUB_SECURITY_TYPE_FUND_GRADED   = 44  # 分级子基金
    OES_SUB_SECURITY_TYPE_FUND_REITS    = 45  # 基础设施基金
    OES_SUB_SECURITY_TYPE_FUND_MAX      = 46  # 基金类证券子类型最大值

    OES_SUB_SECURITY_TYPE_OPTION_MIN    = 50  # 期权类证券子类型最小值
    OES_SUB_SECURITY_TYPE_OPTION_ETF    = 51  # ETF期权
    OES_SUB_SECURITY_TYPE_OPTION_STOCK  = 52  # 个股期权
    OES_SUB_SECURITY_TYPE_OPTION_MAX    = 53  # 期权类证券子类型最大值

    OES_SUB_SECURITY_TYPE_MGR_MIN       = 90  # 管理类证券子类型最小值
    OES_SUB_SECURITY_TYPE_MGR_SSE_DESIGNATION \
                                        = 91  # 指定登记
    OES_SUB_SECURITY_TYPE_MGR_SSE_RECALL_DESIGNATION \
                                        = 92  # 指定撤消
    OES_SUB_SECURITY_TYPE_MGR_SZSE_DESIGNATION \
                                        = 93  # 托管注册
    OES_SUB_SECURITY_TYPE_MGR_SZSE_CANCEL_DESIGNATION \
                                        = 94  # 托管撤消
    OES_SUB_SECURITY_TYPE_MGR_OPT_EXERCISE_TRANSFER \
                                        = 95  # 期权转处置
    OES_SUB_SECURITY_TYPE_MGR_CRD_COLLATERAL_TRANSFER \
                                        = 96  # 信用担保证券划转
    OES_SUB_SECURITY_TYPE_MGR_MAX       = 97  # 管理类证券子类型最大值

    OES_SUB_SECURITY_TYPE_MAX           = OES_SUB_SECURITY_TYPE_MGR_MAX


class eOesCurrTypeT:
    """
    货币类型
    """
    OES_CURR_TYPE_RMB                   = 0  # 人民币
    OES_CURR_TYPE_HKD                   = 1  # 港币
    OES_CURR_TYPE_USD                   = 2  # 美元
    OES_CURR_TYPE_MAX                   = 3  # 货币种类最大值


class eOesAcctTypeT:
    """
    账户类别定义
    资金账户类别与证券账户类别定义相同
    """
    OES_ACCT_TYPE_NORMAL                = 0  # 普通账户
    OES_ACCT_TYPE_CREDIT                = 1  # 信用账户
    OES_ACCT_TYPE_OPTION                = 2  # 衍生品账户
    OES_ACCT_TYPE_MAX                   = 3  # 账户类别最大值


class eOesAcctStatusT:
    """
    客户状态/证券帐户/资金账户状态
    """
    OES_ACCT_STATUS_NORMAL              = 0  # 正常
    OES_ACCT_STATUS_DISABLED            = 1  # 非正常
    OES_ACCT_STATUS_LOCKED              = 2  # 已锁定


class eOesOwnerTypeT:
    """
    所有者类型 (内部使用)
    """
    OES_OWNER_TYPE_UNDEFINE             = 0  # 未定义
    OES_OWNER_TYPE_PERSONAL             = 1  # 个人投资者
    OES_OWNER_TYPE_EXCHANGE             = 101  # 交易所
    OES_OWNER_TYPE_MEMBER               = 102  # 会员
    OES_OWNER_TYPE_INSTITUTION          = 103  # 机构投资者
    OES_OWNER_TYPE_PROPRIETARY          = 104  # 自营
    OES_OWNER_TYPE_MKT_MAKER            = 105  # 做市商
    OES_OWNER_TYPE_SETTLEMENT           = 106  # 结算机构
    OES_OWNER_TYPE_MAX                  = 107  # 所有者类型的最大值


class eOesOptInvLevelT:
    """
    投资者期权等级
    """
    OES_OPT_INV_LEVEL_UNDEFINE          = 0  # 未定义 (机构投资者)
    OES_OPT_INV_LEVEL_1                 = 1  # 个人投资者-一级交易权限
    OES_OPT_INV_LEVEL_2                 = 2  # 个人投资者-二级交易权限
    OES_OPT_INV_LEVEL_3                 = 3  # 个人投资者-三级交易权限
    OES_OPT_INV_LEVEL_MAX               = 4  # 期权投资人级别最大值


class eOesLimitT:
    """
    权限禁用类型
    """
    OES_LIMIT_BUY                       = 1 << 1  # 禁止买入
    OES_LIMIT_SELL                      = 1 << 2  # 禁止卖出
    OES_LIMIT_RECALL_DESIGNATION        = 1 << 3  # 禁止撤销指定
    OES_LIMIT_DESIGNATION               = 1 << 4  # 禁止转托管
    OES_LIMIT_REPO                      = 1 << 5  # 禁止回购融资
    OES_LIMIT_REVERSE_REPO              = 1 << 6  # 禁止质押式逆回购
    OES_LIMIT_SUBSCRIPTION              = 1 << 7  # 禁止新股认购 (新股/可转债/可交换债认购)
    OES_LIMIT_CONVERTIBLE_BOND          = 1 << 8  # 禁止买入可转债
    OES_LIMIT_MARKET_ORDER              = 1 << 9  # 禁止市价委托 (自动根据市价权限映射)
    OES_LIMIT_BUY_OPEN                  = 1 << 10  # 禁止买入开仓
    OES_LIMIT_SELL_CLOSE                = 1 << 11  # 禁止卖出平仓
    OES_LIMIT_SELL_OPEN                 = 1 << 12  # 禁止卖出开仓
    OES_LIMIT_BUY_CLOSE                 = 1 << 13  # 禁止买入平仓
    OES_LIMIT_COVERED_OPEN              = 1 << 14  # 禁止备兑开仓
    OES_LIMIT_COVERED_CLOSE             = 1 << 15  # 禁止备兑平仓
    OES_LIMIT_UNDERLYING_FREEZE         = 1 << 16  # 禁止标的锁定
    OES_LIMIT_UNDERLYING_UNFREEZE       = 1 << 17  # 禁止标的解锁
    OES_LIMIT_OPTION_EXERCISE           = 1 << 18  # 禁止期权行权
    OES_LIMIT_DEPOSIT                   = 1 << 21  # 禁止入金
    OES_LIMIT_WITHDRAW                  = 1 << 22  # 禁止出金
    OES_LIMIT_SSE_BOND_PLATFORM         = 1 << 23  # 禁止交易沪市债券
    OES_LIMIT_ETF_CREATION              = 1 << 24  # 禁止ETF申购
    OES_LIMIT_ETF_REDEMPTION            = 1 << 25  # 禁止ETF赎回
    OES_LIMIT_INSTANT_CANCEL            = 1 << 26  # 禁止瞬时撤单
    OES_LIMIT_COLLATERAL_TRANSFER_IN    = 1 << 31  # 禁止担保品划入
    OES_LIMIT_COLLATERAL_TRANSFER_OUT   = 1 << 32  # 禁止担保品划出
    OES_LIMIT_MARGIN_BUY                = 1 << 33  # 禁止融资买入
    OES_LIMIT_REPAY_MARGIN_BY_SELL      = 1 << 34  # 禁止卖券还款
    OES_LIMIT_REPAY_MARGIN_DIRECT       = 1 << 35  # 禁止直接还款
    OES_LIMIT_SHORT_SELL                = 1 << 36  # 禁止融券卖出
    OES_LIMIT_REPAY_STOCK_BY_BUY        = 1 << 37  # 禁止买券还券
    OES_LIMIT_REPAY_STOCK_DIRECT        = 1 << 38  # 禁止直接还券
    OES_LIMIT_ALL                       = 0xFFFFFFFFFFFFFFFF  # 全部限制
    OES_LIMIT_OPEN_POSITION_STK         = (OES_LIMIT_BUY
                                           | OES_LIMIT_REPO
                                           | OES_LIMIT_REVERSE_REPO
                                           )  # 现货开仓相关的交易限制集合
    OES_LIMIT_CLOSE_POSITION_STK        = OES_LIMIT_SELL  # 现货平仓相关的交易限制集合
    OES_LIMIT_OPEN_POSITION_OPT         = (OES_LIMIT_BUY_OPEN
                                           | OES_LIMIT_SELL_OPEN
                                           | OES_LIMIT_COVERED_OPEN
                                           | OES_LIMIT_UNDERLYING_FREEZE
                                           )  # 期权开仓相关的交易限制集合
    OES_LIMIT_CLOSE_POSITION_OPT        = (OES_LIMIT_SELL_CLOSE
                                           | OES_LIMIT_BUY_CLOSE
                                           | OES_LIMIT_COVERED_CLOSE
                                           | OES_LIMIT_UNDERLYING_UNFREEZE
                                           )  # 期权平仓相关的交易限制集合
    OES_LIMIT_OPEN_POSITION_CRD         = (OES_LIMIT_BUY
                                           | OES_LIMIT_COLLATERAL_TRANSFER_OUT
                                           | OES_LIMIT_MARGIN_BUY
                                           | OES_LIMIT_SHORT_SELL
                                           | OES_LIMIT_REPAY_STOCK_BY_BUY
                                           )  # 信用开仓相关的交易限制集合
    OES_LIMIT_CLOSE_POSITION_CRD        = (OES_LIMIT_SELL
                                           | OES_LIMIT_COLLATERAL_TRANSFER_IN
                                           | OES_LIMIT_REPAY_MARGIN_BY_SELL
                                           )  # 信用平仓相关的交易限制集合
    OES_LIMIT_COLLATERAL_TRANSFER_CRD   = (OES_LIMIT_COLLATERAL_TRANSFER_IN
                                           | OES_LIMIT_COLLATERAL_TRANSFER_OUT
                                           )  # 信用担保品划转交易限制集合
    OES_LIMIT_OPEN_POSITION_ALL         = (OES_LIMIT_OPEN_POSITION_STK
                                           | OES_LIMIT_OPEN_POSITION_OPT
                                           | OES_LIMIT_OPEN_POSITION_CRD
                                           )  # 开仓相关的所有交易限制集合
    OES_LIMIT_CLOSE_POSITION_ALL        = (OES_LIMIT_CLOSE_POSITION_STK
                                           | OES_LIMIT_CLOSE_POSITION_OPT
                                           | OES_LIMIT_CLOSE_POSITION_CRD
                                           )  # 平仓相关的所有交易限制集合


class eOesTradingPermissionT:
    """
    交易权限的枚举值定义
    """
    OES_PERMIS_MARKET_ORDER             = 1 << 1   # 市价委托
    OES_PERMIS_STRUCTURED_FUND          = 1 << 2   # 分级基金适当性
    OES_PERMIS_BOND_QUALIFIED_INVESTOR  = 1 << 3   # 债券专业投资者

    OES_PERMIS_DELISTING                = 1 << 5   # 退市整理股票
    OES_PERMIS_RISK_WARNING             = 1 << 6   # 风险警示股票

    OES_PERMIS_SINGLE_MARKET_ETF        = 1 << 7   # 单市场ETF申赎
    OES_PERMIS_CROSS_BORDER_ETF         = 1 << 8   # 跨境ETF申赎
    OES_PERMIS_CROSS_MARKET_ETF         = 1 << 9   # 跨市场ETF申赎
    OES_PERMIS_CURRENCY_ETF             = 1 << 10  # 货币ETF申赎

    OES_PERMIS_GEMCDR                   = 1 << 11  # 创业板存托凭证
    OES_PERMIS_GEM_REGISTRATION         = 1 << 12  # 注册制创业板交易
    OES_PERMIS_GEM_UNREGISTRATION       = 1 << 13  # 核准制创业板交易
    OES_PERMIS_SH_HK_STOCK_CONNECT      = 1 << 14  # 沪港通
    OES_PERMIS_SZ_HK_STOCK_CONNECT      = 1 << 15  # 深港通

    OES_PERMIS_HLTCDR                   = 1 << 16  # 沪伦通存托凭证
    OES_PERMIS_CDR                      = 1 << 17  # 存托凭证
    OES_PERMIS_INNOVATION               = 1 << 18  # 创新企业股票
    OES_PERMIS_KSH                      = 1 << 19  # 科创板交易

    OES_PERMIS_BOND_ETF                 = 1 << 20  # 债券ETF申赎
    OES_PERMIS_GOLD_ETF                 = 1 << 21  # 黄金ETF申赎
    OES_PERMIS_COMMODITY_FUTURES_ETF    = 1 << 22  # 商品期货ETF申赎
    OES_PERMIS_GEM_INNOVATION           = 1 << 23  # 创业板创新企业股票

    OES_PERMIS_CONVERTIBLE_BOND         = 1 << 24  # 可转换公司债券
    OES_PERMIS_REITS                    = 1 << 25  # 基础设施基金
    OES_PERMIS_CORPORATE_BOND           = 1 << 26  # 公司债/企业债

    OES_PERMIS_ALL                      = 0xFFFFFFFFFFFFFFFF  # 全部权限


class eOesCustTypeT:
    """
    客户类型定义
    """
    OES_CUST_TYPE_PERSONAL              = 0  # 个人
    OES_CUST_TYPE_INSTITUTION           = 1  # 机构
    OES_CUST_TYPE_PROPRIETARY           = 2  # 自营
    OES_CUST_TYPE_PRODUCT               = 3  # 产品
    OES_CUST_TYPE_MKT_MAKER             = 4  # 做市商
    OES_CUST_TYPE_OTHERS                = 5  # 其他
    OES_CUST_TYPE_MAX                   = 6  # 客户类型的最大值


class eOesSecurityRiskLevelT:
    """
    证券风险等级
    """
    OES_RISK_LEVEL_VERY_LOW             = 0  # 最低风险
    OES_RISK_LEVEL_LOW                  = 1  # 低风险
    OES_RISK_LEVEL_MEDIUM_LOW           = 2  # 中低风险
    OES_RISK_LEVEL_MEDIUM               = 3  # 中风险
    OES_RISK_LEVEL_MEDIUM_HIGH          = 4  # 中高风险
    OES_RISK_LEVEL_HIGH                 = 5  # 高风险
    OES_RISK_LEVEL_VERY_HIGH            = 6  # 极高风险


class eOesInvestorClassT:
    """
    投资者分类
    - A类专业投资者: 满足《证券期货投资者适当性管理办法》第八条 (一)、 (二)、 (三) 点
      比如证券公司、期货公司、基金管理公司、商业银行、保险公司、发行的理财产品等
    - B类专业投资者: 满足《证券期货投资者适当性管理办法》第八条 (四)、 (五) 点
      可以是法人或者其他组织、自然人, 满足一定的净资产和金融资产的要求, 具有相关的投资经验
    - C类专业投资者: 满足《证券期货投资者适当性管理办法》第十一条 (一)、 (二) 点
      由普通投资者主动申请转化而来, 满足一定的净资产和金融资产的要求, 具有相关的投资经验
    """
    OES_INVESTOR_CLASS_NORMAL           = 0  # 普通投资者
    OES_INVESTOR_CLASS_PROFESSIONAL_A   = 1  # A类专业投资者
    OES_INVESTOR_CLASS_PROFESSIONAL_B   = 2  # B类专业投资者
    OES_INVESTOR_CLASS_PROFESSIONAL_C   = 3  # C类专业投资者
    OES_INVESTOR_CLASS_PROFESSIONAL     = 4  # 专业投资者


class eOesClientTypeT:
    """
    客户端类型定义 (内部使用)
    """
    OES_CLIENT_TYPE_UNDEFINED           = 0  # 客户端类型-未定义
    OES_CLIENT_TYPE_INVESTOR            = 1  # 普通投资人
    OES_CLIENT_TYPE_VIRTUAL             = 2  # 虚拟账户 (仅开通行情, 不可交易)


class eOesClientStatusT:
    """
    客户端状态定义 (内部使用)
    """
    OES_CLIENT_STATUS_UNACTIVATED       = 0  # 未激活 (不加载)
    OES_CLIENT_STATUS_ACTIVATED         = 1  # 已激活 (正常加载)
    OES_CLIENT_STATUS_PAUSE             = 2  # 已暂停 (正常加载, 不可交易)
    OES_CLIENT_STATUS_SUSPENDED         = 3  # 已挂起 (不加载)
    OES_CLIENT_STATUS_CANCELLED         = 4  # 已注销 (不加载)


class eOesQualificationClassT:
    """
    投资者适当性管理分类
    """
    OES_QUALIFICATION_PUBLIC_INVESTOR   = 0  # 普通投资者
    OES_QUALIFICATION_QUALIFIED_INVESTOR \
                                        = 1  # 专业投资者
    OES_QUALIFICATION_QUALIFIED_INSTITUTIONAL \
                                        = 2  # 专业投资者中的机构投资者


class eOesSubscribeReportTypeT:
    """
    可订阅的回报消息类型定义
    - 0:      默认回报 (等价于: 0x01,0x02,0x04,0x08,0x10,0x20,0x40)
    - 0x0001: OES业务拒绝 (未通过风控检查等)
    - 0x0002: OES委托已生成 (已通过风控检查)
    - 0x0004: 交易所委托回报 (包括交易所委托拒绝、委托确认和撤单完成通知)
    - 0x0008: 交易所成交回报
    - 0x0010: 出入金委托执行报告 (包括出入金委托拒绝、出入金委托回报)
    - 0x0020: 资金变动信息
    - 0x0040: 持仓变动信息
    - 0x0080: 市场状态信息
    - 0x0100: 通知消息回报
    - 0x0200: 结算单确认消息
    - 0x0400: 融资融券直接还款委托执行报告
    - 0x0800: 融资融券合约变动信息
    - 0x1000: 融资融券合约流水信息
    - 0xFFFF: 所有回报
    """
    # 默认回报
    OES_SUB_RPT_TYPE_DEFAULT            = 0

    # OES业务拒绝 (未通过风控检查等)
    OES_SUB_RPT_TYPE_BUSINESS_REJECT    = 0x01

    # OES委托已生成 (已通过风控检查)
    OES_SUB_RPT_TYPE_ORDER_INSERT       = 0x02

    # 交易所委托回报 (包括交易所委托拒绝、委托确认和撤单完成通知)
    OES_SUB_RPT_TYPE_ORDER_REPORT       = 0x04

    # 交易所成交回报
    OES_SUB_RPT_TYPE_TRADE_REPORT       = 0x08

    # 出入金委托执行报告 (包括出入金委托拒绝、出入金委托回报)
    OES_SUB_RPT_TYPE_FUND_TRSF_REPORT   = 0x10

    # 资金变动信息
    OES_SUB_RPT_TYPE_CASH_ASSET_VARIATION \
                                        = 0x20

    # 持仓变动信息
    OES_SUB_RPT_TYPE_HOLDING_VARIATION  = 0x40

    # 市场状态信息
    OES_SUB_RPT_TYPE_MARKET_STATE       = 0x80

    # 通知消息
    OES_SUB_RPT_TYPE_NOTIFY_INFO        = 0x100

    # 结算单确认消息
    OES_SUB_RPT_TYPE_SETTLEMETN_CONFIRMED \
                                        = 0x200

    # 融资融券直接还款委托执行报告
    OES_SUB_RPT_TYPE_CREDIT_CASH_REPAY_REPORT \
                                        = 0x400

    # 融资融券合约变动信息
    OES_SUB_RPT_TYPE_CREDIT_DEBT_CONTRACT_VARIATION \
                                        = 0x800

    # 融资融券合约流水信息
    OES_SUB_RPT_TYPE_CREDIT_DEBT_JOURNAL \
                                        = 0x1000

    # 所有回报
    OES_SUB_RPT_TYPE_ALL                = 0xFFFF

    # 空数据种类 (可用于不订阅任何数据的场景)
    OES_SUB_RPT_TYPE_NONE               = 0x100000


class eOesLotTypeT:
    """
    OES中签、配号记录类型
    """
    OES_LOT_TYPE_UNDEFINE               = 0  # 未定义的中签、配号记录类型
    OES_LOT_TYPE_FAILED                 = 1  # 配号失败记录
    OES_LOT_TYPE_ASSIGNMENT             = 2  # 配号成功记录
    OES_LOT_TYPE_LOTTERY                = 3  # 中签记录


class eOesLotRejReasonT:
    """
    OES配号失败原因
    """
    OES_LOT_REJ_REASON_DUPLICATE        = 1  # 配号失败-重复申购
    OES_LOT_REJ_REASON_INVALID_DUPLICATE \
                                        = 2  # 配号失败-违规重复
    OES_LOT_REJ_REASON_OFFLINE_FIRST    = 3  # 配号失败-网下在先
    OES_LOT_REJ_REASON_BAD_RECORD       = 4  # 配号失败-不良记录
    OES_LOT_REJ_REASON_UNKNOW           = 5  # 配号失败-未知原因


class eOesNotifySourceT:
    """
    通知消息来源分类
    """
    OES_NOTIFY_SOURCE_UNDEFINE          = 0  # 未定义
    OES_NOTIFY_SOURCE_OES               = 1  # OES 交易系统发起
    OES_NOTIFY_SOURCE_MON               = 2  # MON 监控管理端发起
    OES_NOTIFY_SOURCE_BROKER            = 3  # BROKER 期权经营机构发起
    OES_NOTIFY_SOURCE_EXCHANGE          = 4  # EXCHANGE 交易所发起
    OES_NOTIFY_SOURCE_CSDC              = 5  # CSDC 中国结算发起


class eOesNotifyTypeT:
    """
    通知消息类型
    """
    OES_NOTIFY_TYPE_UNDEFINE            = 0  # 未定义

    # 从MON管理端下发的通知消息
    OES_NOTIFY_TYPE_CONTRACT_EXPIRE     = 1  # 合约即将到期
    OES_NOTIFY_TYPE_CONTRACT_ADJUSTED   = 2  # 合约近期有调整
    OES_NOTIFY_TYPE_UNDERLYING_DR_PROXIMITY \
                                        = 3  # 合约标的即将除权除息
    OES_NOTIFY_TYPE_EXERCISE_DATE_PROXIMITY \
                                        = 4  # 合约临近行权日
    OES_NOTIFY_TYPE_EXERCISED_POSSIBILITY   \
                                        = 5  # 合约可能被行权
    OES_NOTIFY_TYPE_EXERCISE_ASSIGNED   = 6  # 合约被指派行权
    OES_NOTIFY_TYPE_COVERED_NOT_ENOUGH  = 7  # 备兑证券标的不足
    OES_NOTIFY_TYPE_DELIVERY_NOT_ENOUGH = 8  # 交收证券不足
    OES_NOTIFY_TYPE_MARGIN_CALL         = 9  # 追加保证金
    OES_NOTIFY_TYPE_FORCED_CLOSE        = 10  # 强制平仓

    # 由OES主动触发的通知消息
    OES_NOTIFY_TYPE_CRD_COLLATERAL_INFO_UPDATE \
                                        = 61  # 融资融券担保品信息更新
    OES_NOTIFY_TYPE_CRD_UNDERLYING_INFO_UPDATE \
                                        = 62  # 融资融券标的信息更新
    OES_NOTIFY_TYPE_CRD_CASH_POSITION_UPDATE \
                                        = 63  # 融资融券资金头寸信息更新 (暂未启用)
    OES_NOTIFY_TYPE_CRD_SECURITY_POSITION_UPDATE \
                                        = 64  # 融资融券证券头寸信息更新
    OES_NOTIFY_TYPE_CRD_MAINTENANCE_RATIO_UPDATE \
                                        = 65  # 融资融券维持担保比例更新
    OES_NOTIFY_TYPE_CRD_LINE_OF_CERDIT_UPDATE \
                                        = 66  # 融资融券授信额度更新

    OES_NOTIFY_TYPE_OTHERS              = 100  # 其它


class eOesNotifyLevelT:
    """
    通知消息等级
    """
    OES_NOTIFY_LEVEL_UNDEFINE           = 0  # 未定义
    OES_NOTIFY_LEVEL_LOW                = 1  # 较低
    OES_NOTIFY_LEVEL_GENERAL            = 2  # 一般
    OES_NOTIFY_LEVEL_IMPORTANT          = 3  # 重要
    OES_NOTIFY_LEVEL_URGENT             = 4  # 紧急


class eOesNotifyScopeT:
    """
    消息通知范围
    """
    OES_NOTIFY_SCOPE_UNDEFINE           = 0  # 未定义
    OES_NOTIFY_SCOPE_CUST               = 1  # 通知指定客户
    OES_NOTIFY_SCOPE_ALL                = 2  # 通知所有投资者


class eOesCrdDebtJournalTypeT:
    """
    融资融券负债流水类型
    """
    OES_CRD_DEBT_JOURNAL_TYPE_OPEN_POSITION \
                                        = 0  # 合约开仓
    OES_CRD_DEBT_JOURNAL_TYPE_REPAY_MARGIN_BY_SELL \
                                        = 1  # 卖券还款
    OES_CRD_DEBT_JOURNAL_TYPE_REPAY_MARGIN_DIRECT \
                                        = 2  # 直接还款
    OES_CRD_DEBT_JOURNAL_TYPE_REPAY_STOCK_BY_BUY \
                                        = 3  # 买券还券
    OES_CRD_DEBT_JOURNAL_TYPE_REPAY_STOCK_DIRECT \
                                        = 4  # 直接还券
    OES_CRD_DEBT_JOURNAL_TYPE_REPAY_STOCK_BY_CASH \
                                        = 5  # 现金了结融券负债
    OES_CRD_DEBT_JOURNAL_TYPE_REPAY_STOCK_BY_OUTSIDE \
                                        = 6  # 场外了结融券负债
    OES_CRD_DEBT_JOURNAL_TYPE_REPAY_MARGIN_BY_OUTSIDE \
                                        = 7  # 场外了结融资负债
    OES_CRD_DEBT_JOURNAL_TYPE_CONTRACT_POST_PONE \
                                        = 8  # 合约展期(审批)
    OES_CRD_DEBT_JOURNAL_TYPE_OTHER     = 9  # 其它类型


class eOesOrdStatusT:
    """
    订单执行状态定义
    """
    OES_ORD_STATUS_PENDING              = 0  # 待处理 (仅内部使用)
    OES_ORD_STATUS_NEW                  = 1  # 新订单 (风控通过)

    OES_ORD_STATUS_DECLARED             = 2  # 已确认
    OES_ORD_STATUS_PARTIALLY_FILLED     = 3  # 部分成交

    OES_ORD_STATUS_FINAL_MIN            = 4  # 订单终结状态判断标志
    OES_ORD_STATUS_CANCEL_DONE          = 5  # 撤单指令已执行 (适用于撤单请求, 并做为撤单请求的终结状态)
    OES_ORD_STATUS_PARTIALLY_CANCELED   = 6  # 部分撤单 (部分成交, 剩余撤单)
    OES_ORD_STATUS_CANCELED             = 7  # 已撤单
    OES_ORD_STATUS_FILLED               = 8  # 已成交 (全部成交)
    OES_ORD_STATUS_VALID_MAX            = 9

    OES_ORD_STATUS_INVALID_MIN          = 10  # 废单判断标志 (委托状态大于该值的全部为废单)
    OES_ORD_STATUS_INVALID_OES          = 11  # OES内部废单
    OES_ORD_STATUS_INVALID_EXCHANGE     = 12  # 交易所后台废单
    OES_ORD_STATUS_INVALID_TGW_REJECT   = 13  # 交易所前台废单 (因订单不合法而被交易网关拒绝)
    OES_ORD_STATUS_INVALID_TGW_COMM     = 14  # 交易所通信故障 (仅适用于上交所)
    OES_ORD_STATUS_INVALID_TGW_TRY_AGAIN \
                                        = 18  # 因平台尚未开放(非交易时段)而被交易网关拒绝 (@note 前端需要关注该状态, 可以根据需要尝试重新发送委托请求)


class eOesProductTypeT:
    """
    产品类型 (high-level category)
    """
    OES_PRODUCT_TYPE_UNDEFINE           = 0  # 未定义的产品类型
    OES_PRODUCT_TYPE_EQUITY             = 1  # 普通股票/存托凭证/债券/基金/科创板
    OES_PRODUCT_TYPE_BOND_STD           = 2  # 逆回购标准券
    OES_PRODUCT_TYPE_IPO                = 3  # 新股认购
    OES_PRODUCT_TYPE_ALLOTMENT          = 4  # 配股认购
    OES_PRODUCT_TYPE_OPTION             = 5  # 期权


class eOesCrdDebtTypeT:
    """
    融资融券负债类型
    """
    OES_CRD_DEBT_TYPE_UNDEFINE          = 0  # 未定义的负债类型
    OES_CRD_DEBT_TYPE_MARGIN_BUY        = 1  # 融资负债
    OES_CRD_DEBT_TYPE_SHORT_SELL        = 2  # 融券负债
    OES_CRD_DEBT_TYPE_OTHER_DEBT        = 3  # 其它负债


class eOesCrdDebtStatusT:
    """
    融资融券负债状态
    """
    OES_CRD_DEBT_STATUS_UNDEFINE        = 0  # 未定义的负债状态
    OES_CRD_DEBT_STATUS_NOT_TRADE       = 1  # 合约尚未成交
    OES_CRD_DEBT_STATUS_NOT_REPAID      = 2  # 未归还
    OES_CRD_DEBT_STATUS_PARTIALLY_REPAID \
                                        = 3  # 部分归还
    OES_CRD_DEBT_STATUS_EXPIRED         = 4  # 到期未了结

    OES_CRD_DEBT_STATUS_REPAID          = 5  # 客户自行了结
    OES_CRD_DEBT_STATUS_MANNUAL_REPAID  = 6  # 手工了结
    OES_CRD_DEBT_STATUS_NOT_DEBT        = 7  # 未形成负债


class eOesCrdDebtRepayModeT:
    """
    融资融券合同约定的负债归还模式
    """
    OES_CRD_DEBT_REPAY_MODE_UNDEFINE    = 0  # 未定义的负债归还模式
    OES_CRD_DEBT_REPAY_MODE_MATCHING_PRINCIPAL \
                                        = 1  # 按比例归还 (利随本清)
    OES_CRD_DEBT_REPAY_MODE_INTEREST_FIRST \
                                        = 2  # 优先归还息费 (先息后本)
    OES_CRD_DEBT_REPAY_MODE_PRINCIPAL_FIRST \
                                        = 3  # 优先归还本金 (先本后息)
    OES_CRD_DEBT_REPAY_MODE_MAX_COMPACT = 4  # 融资融券合同约定的负债归还模式的最大值
    OES_CRD_DEBT_REPAY_MODE_INTEREST_ONLY \
                                        = 10  # 仅归还息费 (仅适用于API接口 @see OES_CRD_ASSIGNABLE_REPAY_MODE_INTEREST_ONLY)


class eOesCrdDebtPostponeStatusT:
    """
    融资融券负债展期状态
    """
    OES_CRD_DEBT_POSTPONE_STATUS_UNDEFINE \
                                        = 0  # 未定义的展期状态
    OES_CRD_DEBT_POSTPONE_STATUS_APPLICABLE \
                                        = 1  # 可申请
    OES_CRD_DEBT_POSTPONE_STATUS_APPLIED \
                                        = 2  # 已申请
    OES_CRD_DEBT_POSTPONE_STATUS_APPROVED \
                                        = 3  # 审批通过
    OES_CRD_DEBT_POSTPONE_STATUS_UNAPPROVED \
                                        = 4  # 审批不通过
    OES_CRD_DEBT_POSTPONE_STATUS_UNAPPLICABLE \
                                        = 5  # 不可申请


class eOesCrdCashGroupPropertyT:
    """
    头寸性质
    """
    OES_CRD_CASH_GROUP_PROP_UNDEFINE    = 0  # 未定义的头寸性质
    OES_CRD_CASH_GROUP_PROP_PUBLIC      = 1  # 公共头寸
    OES_CRD_CASH_GROUP_PROP_SPECIAL     = 2  # 专项头寸


class eOesOrdMandatoryFlagT:
    """
    委托强制标志
    """
    OES_ORD_MANDATORY_FLAG_NONE         = 0  # 无强制标志
    OES_ORD_MANDATORY_FLAG_DELEGATE     = 1  # 代客下单标志

    OES_ORD_MANDATORY_FLAG_MEMBER_MIN   = 10  # 会员管理委托的最小值
    OES_ORD_MANDATORY_FLAG_LIQUDATION   = 11  # 强制平仓标志
    OES_ORD_MANDATORY_FLAG_MANAGEMENT   = 12  # 管理指令标志
    OES_ORD_MANDATORY_FLAG_MAX          = 13  # 委托强制标志的最大值


class eOesOptPositionTypeT:
    """
    期权持仓类型
    """
    OES_OPT_POSITION_TYPE_UNDEFINE      = 0  # 未定义
    OES_OPT_POSITION_TYPE_LONG          = 1  # 权利方
    OES_OPT_POSITION_TYPE_SHORT         = 2  # 义务方
    OES_OPT_POSITION_TYPE_COVERED       = 3  # 备兑方


class eOesOptContractTypeT:
    """
    期权合约类型 (认购/认沽)
    """
    OES_OPT_CONTRACT_TYPE_UNDEFINE      = 0  # 未定义
    OES_OPT_CONTRACT_TYPE_CALL          = 1  # 认购
    OES_OPT_CONTRACT_TYPE_PUT           = 2  # 认沽


class eOesOptDeliveryTypeT:
    """
    期权交割方式 (证券结算/现金结算, 适用于深交所)
    """
    OES_OPT_DELIVERY_TYPE_UNDEFINE      = 0  # 未定义
    OES_OPT_DELIVERY_TYPE_SECURITY      = 1  # 证券结算
    OES_OPT_DELIVERY_TYPE_CASH          = 2  # 现金结算


class eOesOptExerciseTypeT:
    """
    期权行权方式 (欧式/美式)
    """
    OES_OPT_EXERCISE_TYPE_E             = 0  # 欧式
    OES_OPT_EXERCISE_TYPE_A             = 1  # 美式
    OES_OPT_EXERCISE_TYPE_B             = 2  # 百慕大式


class eOesOptLimitOpenFlagT:
    """
    限制开仓标志
    """
    OES_OPT_LIMIT_OPEN_FLAG_NORMAL      = 0  # 可以开仓
    OES_OPT_LIMIT_OPEN_FLAG_LIMITED     = 1  # 限制卖出开仓(不包括备兑开仓)和买入开仓


class eOesSecuritySuspFlagT:
    """
    证券禁止交易标识
    """
    OES_SUSPFLAG_NONE                   = 0x0  # 无禁止交易标识
    OES_SUSPFLAG_EXCHANGE               = 0x1  # 因证券连续停牌而禁止交易
    OES_SUSPFLAG_BROKER                 = 0x2  # 因券商设置而禁止交易
    OES_SUSPFLAG_MARKET_CLOSE           = 0x4  # 因闭市而禁止交易


class eOesEtfCashTypeT:
    """
    ETF成份证券现金替代类型
    """
    OES_ETF_CASH_TYPE_UNUSABLE          = 0  # 不可用替代资金 (目前仅用于上交所ETF赎回业务中的港市替代资金类型)
    OES_ETF_CASH_TYPE_SSE_HK            = 1  # 上交所ETF的港市替代资金 (目前仅用于申购, 赎回时的港市替代资金类型为 OES_ETF_CASH_TYPE_UNUSABLE)

    OES_ETF_CASH_TYPE_NORMAL            = 11  # 普通替代资金 (不区分市场的替代资金; 深交所ETF申赎业务中的替代资金为此类型)
    OES_ETF_CASH_TYPE_SSE_SH            = 12  # 上交所ETF的沪市替代资金
    OES_ETF_CASH_TYPE_SSE_SZ            = 13  # 上交所ETF的深市和京市替代资金
    OES_ETF_CASH_TYPE_SSE_OTHER         = 14  # 上交所ETF的其他市场替代资金


class eOesSecurityIssueTypeT:
    """
    产品发行方式
    """
    OES_ISSUE_TYPE_UNDEFINE             = 0  # 未定义的发行方式
    OES_ISSUE_TYPE_MKT_QUOTA            = 1  # 按市值限额申购 (检查认购限额, 不预冻结资金)
    OES_ISSUE_TYPE_CASH                 = 2  # 增发资金申购 (不检查认购限额, 预冻结资金)
    OES_ISSUE_TYPE_CREDIT               = 3  # 信用申购 (不检查认购限额, 不预冻结资金)


class eOesSecurityAttributeT:
    """
    证券属性的枚举值定义
    """
    OES_SECURITY_ATTR_NONE              = 0       # 无特殊属性
    OES_SECURITY_ATTR_INNOVATION        = 1 << 0  # 创新企业
    OES_SECURITY_ATTR_KSH               = 1 << 1  # 科创板标记


class eOesSecurityLevelT:
    """
    证券级别
    """
    OES_SECURITY_LEVEL_UNDEFINE         = 0
    OES_SECURITY_LEVEL_N                = 1  # 正常证券
    OES_SECURITY_LEVEL_XST              = 2  # *ST股
    OES_SECURITY_LEVEL_ST               = 3  # ST股
    OES_SECURITY_LEVEL_P                = 4  # 退市整理证券
    OES_SECURITY_LEVEL_T                = 5  # 退市转让证券
    OES_SECURITY_LEVEL_U                = 6  # 优先股
    OES_SECURITY_LEVEL_B                = 7  # B级基金


class eOesPricingMethodT:
    """
    计价方式
    """
    OES_PRICING_METHOD_UNDEFINE         = 0  # 未定义的计价方式
    OES_PRICING_METHOD_CLEAN            = 1  # 净价
    OES_PRICING_METHOD_DIRTY            = 2  # 全价


class eOesAuctionLimitTypeT:
    """
    有效竞价范围限制类型
    """
    OES_AUCTION_LIMIT_TYPE_NONE         = 0  # 无竞价范围限制
    OES_AUCTION_LIMIT_TYPE_RATE         = 1  # 按幅度限制 (百分比)
    OES_AUCTION_LIMIT_TYPE_ABSOLUTE     = 2  # 按价格限制 (绝对值)


class eOesAuctionReferPriceTypeT:
    """
    有效竞价范围基准价类型
    """
    OES_AUCTION_REFER_PRICE_TYPE_UNDEFINE \
                                        = 0  # 未定义的基准价类型
    OES_AUCTION_REFER_PRICE_TYPE_LAST   = 1  # 最近价
    OES_AUCTION_REFER_PRICE_TYPE_BEST   = 2  # 对手方最优价 (买委托以卖一为基准价, 卖委托以买一为基准价)
    OES_AUCTION_REFER_PRICE_TYPE_SSE_BEST \
                                        = 3  # 买一卖一价 (仅适用于上交所)
    # 即: 申报价格不高于即时揭示的最低卖出价格的110%且不低于即时揭示的最高买入价格的90%；
    #     同时不高于上述最高申报价与最低申报价平均数的130%且不低于该平均数的70%


class eOesEtfAllCashFlagT:
    """
    ETF是否支持现金申赎标志
    """
    OES_ETF_ALL_CASH_FLAG_UNDERLYING    = 0  # 仅支持实物申赎
    OES_ETF_ALL_CASH_FLAG_CASH          = 1  # 仅支持现金申赎(包括黄金ETF)


class eOesEtfSubFlagT:
    """
    ETF成份证券现金替代标志
    """
    OES_ETF_SUBFLAG_FORBID_SUB          = 0  # 禁止现金替代 (必须有证券)
    OES_ETF_SUBFLAG_ALLOW_SUB           = 1  # 可以进行现金替代(先用证券, 如证券不足可用现金替代)
    OES_ETF_SUBFLAG_MUST_SUB            = 2  # 必须用现金替代
    OES_ETF_SUBFLAG_SZ_REFUND_SUB       = 3  # 该证券为深市或京市证券, 退补现金替代
    OES_ETF_SUBFLAG_SZ_MUST_SUB         = 4  # 该证券为深市或京市证券, 必须现金替代
    OES_ETF_SUBFLAG_OTHER_REFUND_SUB    = 5  # 成份证券退补现金替代
    OES_ETF_SUBFLAG_OTHER_MUST_SUB      = 6  # 成份证券必须现金替代
    OES_ETF_SUBFLAG_HK_REFUND_SUB       = 7  # 港市退补现金替代 (仅适用于跨沪深港ETF产品)
    OES_ETF_SUBFLAG_HK_MUST_SUB         = 8  # 港市必须现金替代 (仅适用于跨沪深港ETF产品)


class eOesExecTypeT:
    """
    OES执行类型
    """
    OES_EXECTYPE_UNDEFINE               = 0  # 未定义的执行类型
    OES_EXECTYPE_INSERT                 = 1  # 已接收 (OES已接收)
    OES_EXECTYPE_CONFIRMED              = 2  # 已确认 (交易所已确认/出入金主柜台已确认)
    OES_EXECTYPE_CANCELLED              = 3  # 已撤单 (原始委托的撤单完成回报)
    OES_EXECTYPE_AUTO_CANCELLED         = 4  # 自动撤单 (市价委托发生自动撤单后的委托回报)
    OES_EXECTYPE_REJECT                 = 5  # 拒绝 (OES拒绝/交易所废单/出入金主柜台拒绝)
    OES_EXECTYPE_TRADE                  = 6  # 成交 (成交回报)
    OES_EXECTYPE_REPAY                  = 7  # 归还 (融资融券业务的合约归还回报)
    OES_EXECTYPE_TIMER                  = 8  # 定时执行
    OES_EXECTYPE_MAX                    = 9  # 执行类型最大值
