# -*- coding: utf-8 -*-
"""
交易api使用样例 (现货业务)
"""
import sys
import time

sys.path.append('../')

"""
@note 请从 trade_api 中引入交易API相关的结构体, 否则兼容性将无法得到保证
"""
from vendor.trade_api import (
    # spk_util.py
    OesApiRemoteCfgT,

    # oes_base_constants.py
    eOesBuySellTypeT, eOesPlatformIdT,
    eOesMarketIdT, eOesExchangeIdT,
    eOesFundTrsfDirectT, eOesFundTrsfTypeT,
    eOesOrdTypeT, eOesOrdTypeSzT, eOesOrdTypeShT,
    eOesSecurityTypeT, eOesSubSecurityTypeT, eOesSubscribeReportTypeT,

    # oes_base_model_credit.py
    # oes_base_model_option_.py

    # oes_base_model.py
    OesOrdReqT, OesOrdCancelReqT, OesFundTrsfReqT,
    OesOrdCnfmT, OesCashAssetItemT,

    # oes_qry_packets.py
    OesBrokerParamsInfoT, OesClientOverviewT, OesCustOverviewT,
    OesCashAcctOverviewT, OesInvAcctOverviewT,
    OesQryOrdFilterT, OesQryTrdFilterT,
    OesQryStkHoldingFilterT, OesQryStockFilterT,
    OesQryCashAssetFilterT, OesQryEtfComponentFilterT,
    OesQryEtfFilterT, OesQryMarketStateFilterT,

    # oes_qry_packets_credit.py
    # oes_qry_packets_option.py
    # oes_packets.py

    # oes_api.py
    OesClientApi,
    OESAPI_CFG_DEFAULT_SECTION,
    OESAPI_CFG_DEFAULT_KEY_ORD_ADDR,
    OESAPI_CFG_DEFAULT_KEY_RPT_ADDR
)

from my_spi import (
    OesClientMySpi
)


def query_sample(api: OesClientApi) -> None:
    """
    查询接口使用样例
    - @note 批量查询到的总条数为0时, 不会触发回调函数 (对应my_spi.py中的函数)

    Args:
        api (OesClientApi): [oes-api客户端]
    """

    """ 查询成交样例 """
    # 查询全部成交信息
    api.query_trade()

    # 查询上海A股的成交
    api.query_trade(
        qry_filter=OesQryTrdFilterT(
            mktId=eOesMarketIdT.OES_MKT_SH_ASHARE))

    # 查询客户端环境号为1的所有成交
    api.query_trade(
        qry_filter=OesQryTrdFilterT(
            clEnvId=1))


    """ 查询委托样例 """
    # 查询全部委托
    api.query_order()

    # 查询14:10 到 14:20 之间的所有委托
    api.query_order(
        qry_filter=OesQryOrdFilterT(
            startTime=141000000, endTime=142000000))

    # 查询债券的所有委托
    api.query_order(
        qry_filter=OesQryOrdFilterT(
            securityType=eOesSecurityTypeT.OES_SECURITY_TYPE_BOND))


    """ 查询持仓信息 """
    # 查询 上海A股市场证券代码为 600000 的持仓
    api.query_stk_holding(
        qry_filter=OesQryStkHoldingFilterT(
            mktId=eOesMarketIdT.OES_MKT_SH_ASHARE,
            securityId=b"600000"))

    # 查询 上海A股市场的所有持仓
    api.query_stk_holding(qry_filter=OesQryStkHoldingFilterT(mktId=eOesMarketIdT.OES_MKT_SH_ASHARE))

    # 查询 沪深两市 所有股票持仓
    api.query_stk_holding()


    """ 查询客户端总览信息 """
    overview: OesClientOverviewT = api.get_client_overview()
    if overview:
        print(f">>> 客户端总览信息: 客户端编号[{overview.clientId}], "
              f"客户端类型[{overview.clientType}], "
              f"客户端状态[{overview.clientStatus}], "
              f"客户端名称[{overview.clientName.decode()}], "
              f"客户端适用的业务范围[{overview.businessScope}], "
              f"上海现货对应PBU[{overview.sseStkPbuId,}], "
              f"深圳现货对应PBU[{overview.szseStkPbuId}], "
              f"委托通道流控阈值[{overview.ordTrafficLimit}], "
              f"查询通道流控阈值[{overview.qryTrafficLimit}], "
              f"当前节点资金配比[{overview.initialCashAssetRatio,}], "
              f"是否支持两地交易内部资金划拨[{overview.isSupportInternalAllot}], "
              f"是否支持与银行间银证转帐[{overview.isSupportBankFundTrsf}],"
              f"关联的客户数量[{overview.associatedCustCnt}]")

        associated_cust_cn: int = overview.associatedCustCnt
        for i in range(associated_cust_cn):
            cust_item: OesCustOverviewT = overview.custItems[i]
            print(f"    >>> 客户总览信息: 客户代码[{cust_item.custId.decode()}], "
                  f"客户状态[{cust_item.status}], "
                  f"风险评级[{cust_item.riskLevel}], "
                  f"营业部代码[{cust_item.branchId}], "
                  f"客户姓名[{cust_item.custName}]")

            cash_acct: OesCashAcctOverviewT = cust_item.cashAcct
            if cash_acct.isValid:
                print(
                    f"        >>> 资金账户总览: 资金账户[{cash_acct.cashAcctId.decode()}], "
                    f"资金类型[{cash_acct.cashType}], "
                    f"账户状态[{cash_acct.cashAcctStatus}], "
                    f"出入金是否禁止[{cash_acct.isFundTrsfDisabled}]")

            inv_acct: OesInvAcctOverviewT = cust_item.sseInvAcct
            if inv_acct.isValid:
                print(f"        >>> 股东账户总览: "
                      f"股东账户代码[{inv_acct.invAcctId}], "
                      f"市场代码[{inv_acct.mktId}], "
                      f"账户状态[{inv_acct.status}], "
                      f"是否禁止交易[{inv_acct.isTradeDisabled}], "
                      f"席位号[{inv_acct.pbuId}], "
                      f"当日累计有效交易类委托笔数[{inv_acct.trdOrdCnt}], "
                      f"当日累计有效非交易类委托笔数[{inv_acct.nonTrdOrdCnt}], "
                      f"当日累计有效撤单笔数[{inv_acct.cancelOrdCnt}], "
                      f"当日累计被OES拒绝的委托笔数[{inv_acct.oesRejectOrdCnt}], "
                      f"当日累计被交易所拒绝的委托笔数[{inv_acct.exchRejectOrdCnt}], "
                      f"当日累计成交笔数[{inv_acct.trdCnt}]")

            inv_acct: OesInvAcctOverviewT = cust_item.szseInvAcct
            if inv_acct.isValid:
                print(f"        >>> 股东账户总览: "
                      f"股东账户代码[{inv_acct.invAcctId}], "
                      f"市场代码[{inv_acct.mktId}], "
                      f"账户状态[{inv_acct.status}], "
                      f"是否禁止交易[{inv_acct.isTradeDisabled}], "
                      f"席位号[{inv_acct.pbuId}], "
                      f"当日累计有效交易类委托笔数[{inv_acct.trdOrdCnt}], "
                      f"当日累计有效非交易类委托笔数[{inv_acct.nonTrdOrdCnt}], "
                      f"当日累计有效撤单笔数[{inv_acct.cancelOrdCnt}], "
                      f"当日累计被OES拒绝的委托笔数[{inv_acct.oesRejectOrdCnt}], "
                      f"当日累计被交易所拒绝的委托笔数[{inv_acct.exchRejectOrdCnt}], "
                      f"当日累计成交笔数[{inv_acct.trdCnt}]")


    """ 查询客户信息 """
    api.query_cust_info()


    """ 查询资金账户信息 """
    # 查询 所有关联资金账户的资金信息
    api.query_cash_asset()

    # 查询 指定资金账户的资金信息
    api.query_cash_asset(
        qry_filter=OesQryCashAssetFilterT(
            cashAcctId=b"******"))


    """ 查询两地交易对端资金账户信息 """
    # 查询两地交易时对端结点的资金信息
    cash_asset: OesCashAssetItemT = \
        api.get_colocation_peer_cash_asset(
            cash_acct_id="")
    if cash_asset:
        print(f">>> 查询到对端节点的资金信息: "
              f"资金账户代码[{cash_asset.cashAcctId.decode()}], "
              f"客户代码[{cash_asset.custId.decode()}], "
              f"币种[{cash_asset.cashType}], "
              f"资金类型[{cash_asset.currType}], "
              f"期初余额[{cash_asset.beginningBal}], "
              f"期初可用[{cash_asset.beginningAvailableBal}], "
              f"期初可取[{cash_asset.beginningDrawableBal}], "
              f"不可用[{cash_asset.disableBal}], "
              f"累计存入[{cash_asset.totalDepositAmt}], "
              f"累计提取[{cash_asset.totalWithdrawAmt}], "
              f"当前提取冻结[{cash_asset.withdrawFrzAmt}], "
              f"累计卖出[{cash_asset.totalSellAmt}], "
              f"累计买入[{cash_asset.totalBuyAmt}], "
              f"当前买冻结[{cash_asset.buyFrzAmt}], "
              f"累计费用[{cash_asset.totalFeeAmt}], "
              f"当前费用冻结[{cash_asset.feeFrzAmt}], "
              f"当前维持保证金[{cash_asset.marginAmt}], "
              f"当前保证金冻结[{cash_asset.marginFrzAmt}], "
              f"当前余额[{cash_asset.currentTotalBal}], "
              f"当前可用[{cash_asset.currentAvailableBal}],"
              f"当前可取[{cash_asset.currentDrawableBal}]")


    """ 查询股票产品 """
    # 查询 证券代码为 600000 的产品信息(不指定市场和证券类型及子类型)
    api.query_stock(
        qry_filter=OesQryStockFilterT(
            securityId=b"600000",
            mktId=eOesMarketIdT.OES_MKT_UNDEFINE,
            securityType=eOesSecurityTypeT.OES_SECURITY_TYPE_UNDEFINE,
            subSecurityType=eOesSubSecurityTypeT.OES_SUB_SECURITY_TYPE_UNDEFINE))

    # 查询 上海A股市场 的所有产品信息
    api.query_stock(
        qry_filter=OesQryStockFilterT(
            mktId=eOesMarketIdT.OES_MKT_SH_ASHARE,
            securityType=eOesSecurityTypeT.OES_SECURITY_TYPE_UNDEFINE,
            subSecurityType=eOesSubSecurityTypeT.OES_SUB_SECURITY_TYPE_UNDEFINE))


    """ 查询ETF产品信息 """
    # 查询所有上海市场的ETF产品信息
    api.query_etf(
        qry_filter=OesQryEtfFilterT(
            mktId=eOesMarketIdT.OES_MKT_SH_ASHARE))


    """ 查询ETF成分信息 """
    # 查询基金代码为512320的成分信息
    api.query_etf_component(
        qry_filter=OesQryEtfComponentFilterT(fundId=b"512320"))


    """ 查询新股申购中签信息 """
    # 查询 新股申购中签信息
    api.query_lot_winning()


    """ 查询佣金信息 """
    api.query_commission_rate()


    """ 查询通知消息 """
    api.query_notify_info()


    """ 查询券商信息 """
    broker_info: OesBrokerParamsInfoT = api.query_broker_params_info()
    if broker_info:
        print(
            f">>> 券商参数信息: 券商名称[{broker_info.brokerName.decode()}], "
            f"券商电话[{broker_info.brokerPhone.decode()}], "
            f"券商网址[{broker_info.brokerWebsite.decode()}], "
            f"API兼容的最低协议版本号[{broker_info.apiMinVersion.decode()}], "
            f"客户端最新版本号[{broker_info.clientVersion.decode()}], "
            f"限制客户端修改密码的结束时间 (HHMMSSsss)[{broker_info.forbidChangePwdEndTime}], "
            f"限制客户端修改密码的开始时间 (HHMMSSsss)[{broker_info.forbidChangePwdBeginTime}], "
            f"客户端密码允许的最小长度[{broker_info.minClientPasswordLen}], "
            f"客户端密码强度级别[{broker_info.clientPasswordStrength}], "
            f"服务端支持的业务范围[{broker_info.businessScope}], "
            f"当前会话对应的业务类型[{broker_info.currentBusinessType}], "
            f"服务端是否支持两地交易内部资金划拨[{broker_info.isSupportInternalAllot}], "
            f"服务端是否支持与银行间银证转帐[{broker_info.isSupportBankFundTrsf}], "
            f"客户代码[{broker_info.custId.decode()}], "
            f"证风险警示板证券单日买入数量限制[{broker_info.sseRiskWarningSecurityBuyQtyLimit}], "
            f"深证风险警示板证券单日买入数量限制[{broker_info.szseRiskWarningSecurityBuyQtyLimit}]")

    """ 查询市场状态 """
    # 查询 深交所 现货集中竞价平台 市场状态
    api.query_market_state(
        qry_filter=OesQryMarketStateFilterT(
            exchId=eOesExchangeIdT.OES_EXCH_SZSE,
            platformId=eOesPlatformIdT.OES_PLATFORM_CASH_AUCTION))


    """ 查询API版本 """
    print(">>> API版本信息: ", api.get_api_version())


    """ 查询当前交易日 """
    print(">>> 服务端交易日:", api.get_trading_day())


def order_sample(api: OesClientApi) -> None:
    """
    委托接口使用样例
    - 委托接口分为单笔委托申报和批量委托申报
    - 委托申报为单向异步方式发送, 申报处理结果将通过回报数据返回

    Args:
        api (OesClientApi): [oes-api客户端]
    """

    # 上海A股市场的买卖
    # - 以 12.67元 购买 浦发银行(600000) 100股
    ret = api.send_order(
        req=OesOrdReqT(
            clSeqNo=api.get_next_cl_seq_no(),
            mktId=eOesMarketIdT.OES_MKT_SH_ASHARE,
            securityId=b"600000",
            bsType=eOesBuySellTypeT.OES_BS_TYPE_BUY,
            ordType=eOesOrdTypeShT.OES_ORD_TYPE_SH_LMT,
            ordPrice=126700,
            ordQty=100))
    if ret < 0:
        print("发送委托请求失败, 参数错误? 请参考日志信息检查相关数据是否合法!")
        return


    # 深圳A股市场的买卖
    # - 以 市价 卖出 平安银行(000001) 200股
    ret = api.send_order(
        req=OesOrdReqT(
            clSeqNo=api.get_next_cl_seq_no(),
            mktId=eOesMarketIdT.OES_MKT_SZ_ASHARE,
            securityId=b"000001",
            bsType=eOesBuySellTypeT.OES_BS_TYPE_SELL,
            ordType=eOesOrdTypeSzT.OES_ORD_TYPE_SZ_MTL_BEST,
            ordQty=200))
    if ret < 0:
        print("发送委托请求失败, 参数错误? 请参考日志信息检查相关数据是否合法!")
        return


    # 上海债券买入
    # - 以 1000.00 元购买 山能YK01(115627) 10张
    ret = api.send_order(
        req=OesOrdReqT(
            clSeqNo=api.get_next_cl_seq_no(),
            mktId=eOesMarketIdT.OES_MKT_SH_ASHARE,
            securityId=b"198609",
            bsType=eOesBuySellTypeT.OES_BS_TYPE_BUY,
            ordType=eOesOrdTypeT.OES_ORD_TYPE_LMT,
            ordPrice=10000000,
            ordQty=10))
    if ret < 0:
        print("发送委托请求失败, 参数错误? 请参考日志信息检查相关数据是否合法!")
        return


    # 上海债券卖出
    # - 以 市价(最优五档即使成交剩余转限价委托) 卖出 中置01次(199857) 10张
    ret = api.send_order(
        req=OesOrdReqT(
            clSeqNo=api.get_next_cl_seq_no(),
            mktId=eOesMarketIdT.OES_MKT_SH_ASHARE,
            securityId=b"199857",
            bsType=eOesBuySellTypeT.OES_BS_TYPE_SELL,
            ordType=eOesOrdTypeShT.OES_ORD_TYPE_SH_MTL_BEST_5,
            ordQty=10))
    if ret < 0:
        print("发送委托请求失败, 参数错误? 请参考日志信息检查相关数据是否合法!")
        return


    # 上海ETF基金的申购
    # - 以 市价(最优五档剩余转撤销) 申购 能源ETF (561260) 1000份
    ret = api.send_order(
        req=OesOrdReqT(
            clSeqNo=api.get_next_cl_seq_no(),
            mktId=eOesMarketIdT.OES_MKT_SH_ASHARE,
            securityId=b"561260",
            bsType=eOesBuySellTypeT.OES_BS_TYPE_CREATION,
            ordType=eOesOrdTypeT.OES_ORD_TYPE_FAK_BEST_5,
            ordQty=1000))
    if ret < 0:
        print("发送委托请求失败, 参数错误? 请参考日志信息检查相关数据是否合法!")
        return


    # 上海ETF基金的赎回
    # - 以 市价(最优五档剩余转撤销) 赎回 能源ETF (561260) 1000份
    ret = api.send_order(
        req=OesOrdReqT(
            clSeqNo=api.get_next_cl_seq_no(),
            mktId=eOesMarketIdT.OES_MKT_SH_ASHARE,
            securityId=b"561260",
            bsType=eOesBuySellTypeT.OES_BS_TYPE_REDEMPTION,
            ordType=eOesOrdTypeShT.OES_ORD_TYPE_SH_FAK_BEST_5,
            ordQty=1000))
    if ret < 0:
        print("发送委托请求失败, 参数错误? 请参考日志信息检查相关数据是否合法!")
        return


    # 上海市场的逆回购交易
    # - 以 1.235 的报价做 10万元 GC001(204001)逆回购
    #   - 逆回购每张标准券100元，委托份数填 (10万元 除以 100元/张 =) 1000张
    #   - 上证逆回购报价单位是0.005，份数单位是1000张
    ret = api.send_order(
        req=OesOrdReqT(
            clSeqNo=api.get_next_cl_seq_no(),
            mktId=eOesMarketIdT.OES_MKT_SH_ASHARE,
            securityId=b"204001",
            bsType=eOesBuySellTypeT.OES_BS_TYPE_REVERSE_REPO,
            ordType=eOesOrdTypeT.OES_ORD_TYPE_LMT,
            ordQty=1000,
            ordPrice=12350))
    if ret < 0:
        print("发送委托请求失败, 参数错误? 请参考日志信息检查相关数据是否合法!")
        return


    # 深圳市场的逆回购交易
    # - 以 4.321 的报价做 1千元 R-001(131810)逆回购
    #   - 逆回购每张标准券100元，委托份数填 (1千元 除以 100元/张 =) 10张
    #   - 深证逆回购报价单位是0.001，份数单位是10张
    ret = api.send_order(
        req=OesOrdReqT(
            clSeqNo=api.get_next_cl_seq_no(),
            mktId=eOesMarketIdT.OES_MKT_SZ_ASHARE,
            securityId=b"131810",
            bsType=eOesBuySellTypeT.OES_BS_TYPE_REVERSE_REPO,
            ordType=eOesOrdTypeT.OES_ORD_TYPE_LMT,
            ordQty=10,
            ordPrice=43210))
    if ret < 0:
        print("发送委托请求失败, 参数错误? 请参考日志信息检查相关数据是否合法!")
        return


    # 深圳市场的新股认购
    # - 认购 迈为股份(300751) 500股
    # - 新股申购额度通过 查询股东账户信息(OesApi_QueryInvAcct)接口 返回信息中的OesInvAcctItemT.subscriptionQuota 来获取
    ret = api.send_order(
        req=OesOrdReqT(
            clSeqNo=api.get_next_cl_seq_no(),
            mktId=eOesMarketIdT.OES_MKT_SZ_ASHARE,
            securityId=b"300751",
            bsType=eOesBuySellTypeT.OES_BS_TYPE_SUBSCRIPTION,
            ordType=eOesOrdTypeT.OES_ORD_TYPE_LMT,
            ordQty=500))
    if ret < 0:
        print("发送委托请求失败, 参数错误? 请参考日志信息检查相关数据是否合法!")
        return


    # 深圳市场的配股认购
    # - 以 发行价 认购 万顺配债(380057) 500股
    ret = api.send_order(
        req=OesOrdReqT(
            clSeqNo=api.get_next_cl_seq_no(),
            mktId=eOesMarketIdT.OES_MKT_SZ_ASHARE,
            securityId=b"380057",
            bsType=eOesBuySellTypeT.OES_BS_TYPE_ALLOTMENT,
            ordType=eOesOrdTypeT.OES_ORD_TYPE_LMT,
            ordQty=500))
    if ret < 0:
        print("发送委托请求失败, 参数错误? 请参考日志信息检查相关数据是否合法!")
        return


def cancel_order_sample(api: OesClientApi) -> None:
    """
    撤单接口使用样例
      - 1. 可以通过指定 "待撤订单的客户订单编号(origClOrdId)" 予以撤单
      - 2. 可以通过指定 "待撤订单的客户委托流水号(origClSeqNo) + 待撤订单的客户端环境号(origClEnvId)" 予以撤单
      - 如下交易类型不支持撤单:
        - 上海期权市场的标的锁定/解锁

    Args:
        api (OesClientApi): [oes-api客户端]
    """

    # 定义 orig_order 作为模拟的待撤委托
    # 真实场景中，待撤委托的clOrdId需要通过回报消息获取
    orig_order: OesOrdCnfmT = OesOrdCnfmT(
        mktId=eOesMarketIdT.OES_MKT_SH_ASHARE,
        clEnvId=1,
        clSeqNo=11,
        clOrdId=111)


    # 通过待撤委托的 clOrdId 进行撤单
    ret = api.send_cancel_order(
        req=OesOrdCancelReqT(
            clSeqNo=api.get_next_cl_seq_no(),
            mktId=orig_order.mktId,
            origClOrdId=orig_order.clOrdId))
    if ret < 0:
        print("发送撤单委托请求失败, 参数错误? 请参考日志信息检查相关数据是否合法!")
        return


    # 通过待撤委托的 clSeqNo + clEnvId 进行撤单
    ret = api.send_cancel_order(
        req=OesOrdCancelReqT(
            clSeqNo=api.get_next_cl_seq_no(),
            mktId=orig_order.mktId,
            origClSeqNo=orig_order.clSeqNo,
            origClEnvId=orig_order.clEnvId))
    if ret < 0:
        print("发送撤单委托请求失败, 参数错误? 请参考日志信息检查相关数据是否合法!")
        return


def fund_transfer_sample(api: OesClientApi) -> None:
    """
    出入金接口使用样例

    Args:
        api (OesClientApi): [oes客户端]
    """
    # 从OES出金到银行
    # @note trdPasswd和trsfPasswd的值类型是bytes
    ret = api.send_fund_trsf(
        req=OesFundTrsfReqT(
            clSeqNo=api.get_next_cl_seq_no(),
            direct=eOesFundTrsfDirectT.OES_FUND_TRSF_DIRECT_OUT,
            fundTrsfType=eOesFundTrsfTypeT.OES_FUND_TRSF_TYPE_OES_BANK,
            occurAmt=10000,
            trdPasswd=b"xxxxxx",
            trsfPasswd=b"xxxxxx"))
    if ret < 0:
        print("发送出入金委托请求失败, 参数错误? 请参考日志信息检查相关数据是否合法!")
        return

    # 从银行入金到主柜
    # @note trdPasswd和trsfPasswd的值类型是bytes
    ret = api.send_fund_trsf(
        req=OesFundTrsfReqT(
            clSeqNo=api.get_next_cl_seq_no(),
            direct=eOesFundTrsfDirectT.OES_FUND_TRSF_DIRECT_IN,
            fundTrsfType=eOesFundTrsfTypeT.OES_FUND_TRSF_TYPE_COUNTER_BANK,
            occurAmt=10000,
            trdPasswd=b"xxxxxx",
            trsfPasswd=b"xxxxxx"))
    if ret < 0:
        print("发送出入金委托请求失败, 参数错误? 请参考日志信息检查相关数据是否合法!")
        return


    # 从主柜调拨资金到OES
    ret = api.send_fund_trsf(
        req=OesFundTrsfReqT(
            clSeqNo=api.get_next_cl_seq_no(),
            direct=eOesFundTrsfDirectT.OES_FUND_TRSF_DIRECT_IN,
            fundTrsfType=eOesFundTrsfTypeT.OES_FUND_TRSF_TYPE_OES_COUNTER,
            occurAmt=10000))
    if ret < 0:
        print("发送出入金委托请求失败, 参数错误? 请参考日志信息检查相关数据是否合法!")
        return


    # 从本端转出资金到对端OES结点
    ret = api.send_fund_trsf(
        req=OesFundTrsfReqT(
            clSeqNo=api.get_next_cl_seq_no(),
            direct=eOesFundTrsfDirectT.OES_FUND_TRSF_DIRECT_OUT,
            fundTrsfType=eOesFundTrsfTypeT.OES_FUND_TRSF_TYPE_OES_TO_OES,
            occurAmt=10000))
    if ret < 0:
        print("发送出入金委托请求失败, 参数错误? 请参考日志信息检查相关数据是否合法!")
        return


    # 从对端OES结点转入资金到本端
    ret = api.send_fund_trsf(
        req=OesFundTrsfReqT(
            clSeqNo=api.get_next_cl_seq_no(),
            direct=eOesFundTrsfDirectT.OES_FUND_TRSF_DIRECT_IN,
            fundTrsfType=eOesFundTrsfTypeT.OES_FUND_TRSF_TYPE_OES_TO_OES,
            occurAmt=10000))
    if ret < 0:
        print("发送出入金委托请求失败, 参数错误? 请参考日志信息检查相关数据是否合法!")
        return


def oes_sample_main() -> None:
    """
    OES交易对接的样例代码
    - 通过不同方式添加多个委托通道与多个回报通道, 每个回报通道订阅不同的回报信息
      - add_ord_channel_from_file
      - add_ord_channel
      - add_rpt_channel_from_file
      - add_rpt_channel
    """
    config_file_name: str = './oes_client_stk.conf'
    remote_cfg: OesApiRemoteCfgT = OesApiRemoteCfgT()

    # 1. 创建交易API实例
    api: OesClientApi = OesClientApi(config_file_name)
    # 2. 创建自定义的SPI回调实例
    spi: OesClientMySpi = OesClientMySpi()

    # 3. 将SPI实例注册至API实例中, 以达到通过自定义的回调函数收取交易回报的效果
    # - 未添加默认的委托通道与回报通道, 后续手工添加
    api.register_spi(spi, add_default_channel=False)


    # 4. (出于演示的目的) 分别添加两个委托通道和两个回报通道

    # - 4.1 添加第一个委托通道 (环境号设置为1) (从配置文件中加载通道地址等配置信息)
    ord_channel1 = api.add_ord_channel_from_file(
        channel_tag = "OrdChannel_ClEnvId_1",
        config_file = config_file_name,
        config_section = OESAPI_CFG_DEFAULT_SECTION,
        addr_key = OESAPI_CFG_DEFAULT_KEY_ORD_ADDR,
        user_info = "OrdChannel_ClEnvId_1",
        oes_client_spi = None,
        copy_args = True)
    if not ord_channel1:
        api.release()
        return
    else:
        # 重置委托通道使用的用户名称和密码 (默认会使用配置文件中的设置)
        # - username: 用户名
        # - password: 密码
        #   - 支持通过前缀指定密码类型, 如 md5:PASSWORD, txt:PASSWORD
        ord_channel1.pChannelCfg.contents.remoteCfg.username = b"demo001"
        ord_channel1.pChannelCfg.contents.remoteCfg.password = b"123456"

        # 在Start之前, 可以直接设置通道使用的环境号 (默认会使用配置文件中的设置)
        ord_channel1.pChannelCfg.contents.remoteCfg.clEnvId = 1
    # -------------------------


    # - 4.2 添加第二个委托通道 (环境号设置为2)

    # 从配置文件中加载服务器地址、初始订阅参数等配置信息, 作为配置模版
    if api.parse_config_from_file(
            config_file_name, OESAPI_CFG_DEFAULT_SECTION,
            OESAPI_CFG_DEFAULT_KEY_ORD_ADDR, remote_cfg) is False:
        api.release()
        return

    # 通过代码改写服务器地址配置、用户名、密码等配置信息
    remote_cfg.clEnvId = 2
    remote_cfg.username = b"demo001"
    remote_cfg.password = b"123456"
    remote_cfg.addrCnt = api.parse_addr_list_string(
        "tcp://106.15.58.119:6101, tcp://192.168.0.11:6101",
        remote_cfg.addrList)
    if remote_cfg.addrCnt <= 0:
        print("解析自定义的服务器地址列表失败!")
        api.release()
        return

    ord_channel2 = api.add_ord_channel(
        channel_tag = "OrdChannel_ClEnvId_2",
        remote_cfg = remote_cfg,
        user_info = None,
        oes_client_spi = None,
        copy_args = True)
    if not ord_channel2:
        api.release()
        return
    else:
        # 重置委托通道使用的用户名称和密码 (默认会使用remote_cfg中的设置)
        # - username: 用户名
        # - password: 密码
        #   - 支持通过前缀指定密码类型, 如 md5:PASSWORD, txt:PASSWORD
        ord_channel2.pChannelCfg.contents.remoteCfg.username = b"demo001"
        ord_channel2.pChannelCfg.contents.remoteCfg.password = b"123456"
    # -------------------------


    # - 4.3 添加第一个回报通道 (环境号设置为1) (从配置文件中加载通道地址和回报订阅参数等配置信息)
    rpt_channel1 = api.add_rpt_channel_from_file(
        channel_tag = "RptChannel_ClEnvId_1",
        config_file = config_file_name,
        config_section = OESAPI_CFG_DEFAULT_SECTION,
        addr_key = OESAPI_CFG_DEFAULT_KEY_RPT_ADDR,
        user_info = "RptChannel_ClEnvId_1",
        oes_client_spi = None,
        copy_args = True)
    if not rpt_channel1:
        api.release()
        return
    else:
        # 重置回报通道使用的用户名称和密码 (默认会使用配置文件中的设置)
        # - username: 用户名
        # - password: 密码
        #   - 支持通过前缀指定密码类型, 如 md5:PASSWORD, txt:PASSWORD
        rpt_channel1.pChannelCfg.contents.remoteCfg.username = b"demo001"
        rpt_channel1.pChannelCfg.contents.remoteCfg.password = b"123456"

        # 在Start之前, 可以直接设置通道使用的环境号 (默认会使用配置文件中的设置)
        api.get_channel_subscribe_cfg(rpt_channel1).clEnvId = 1
        api.get_channel_subscribe_cfg(rpt_channel1).rptTypes = \
            eOesSubscribeReportTypeT.OES_SUB_RPT_TYPE_BUSINESS_REJECT \
            | eOesSubscribeReportTypeT.OES_SUB_RPT_TYPE_ORDER_INSERT \
            | eOesSubscribeReportTypeT.OES_SUB_RPT_TYPE_ORDER_REPORT \
            | eOesSubscribeReportTypeT.OES_SUB_RPT_TYPE_TRADE_REPORT \
            | eOesSubscribeReportTypeT.OES_SUB_RPT_TYPE_FUND_TRSF_REPORT

        # lastInMsgSeq: 指定待订阅的回报数据的起始位置
        #   - 等于0, 从头开始推送回报数据(默认值)
        #   - 大于0, 以指定的回报编号为起点, 从该回报编号的下一条数据开始推送
        #   - 小于0, 从最新的数据开始推送回报数据
        rpt_channel1.lastInMsgSeq = -1
    # -------------------------


    # - 4.4 添加第二个回报通道 (环境号设置为2)

    # 从配置文件中加载服务器地址、初始订阅参数等配置信息, 作为配置模版
    if api.parse_config_from_file(
            config_file_name, OESAPI_CFG_DEFAULT_SECTION,
            OESAPI_CFG_DEFAULT_KEY_RPT_ADDR, remote_cfg) is False:
        api.release()
        return

    # 通过代码改写服务器地址配置、用户名、密码等配置信息
    remote_cfg.clEnvId = 2
    remote_cfg.username = b"demo001"
    remote_cfg.password = b"123456"
    remote_cfg.addrCnt = api.parse_addr_list_string(
        "tcp://106.15.58.119:6301, tcp://192.168.0.11:6301",
        remote_cfg.addrList)
    if remote_cfg.addrCnt <= 0:
        print("解析自定义的服务器地址列表失败!")
        api.release()
        return

    rpt_channel2 = api.add_rpt_channel(
        channel_tag = "RptChannel_ClEnvId_2",
        remote_cfg = remote_cfg,
        user_info = None,
        oes_client_spi = None,
        copy_args = True)
    if not rpt_channel2:
        api.release()
        return
    else:
        # 重置回报通道使用的用户名称和密码 (默认会使用remote_cfg中的设置)
        # - username: 用户名
        # - password: 密码
        #   - 支持通过前缀指定密码类型, 如 md5:PASSWORD, txt:PASSWORD
        rpt_channel2.pChannelCfg.contents.remoteCfg.username = b"demo001"
        rpt_channel2.pChannelCfg.contents.remoteCfg.password = b"123456"

        # 在Start之前, 可以直接设置通道使用的环境号 (默认会使用配置文件中的设置)
        api.get_channel_subscribe_cfg(rpt_channel2).clEnvId = 2
        api.get_channel_subscribe_cfg(rpt_channel2).rptTypes = 0

        # lastInMsgSeq: 指定待订阅的回报数据的起始位置
        #   - 等于0, 从头开始推送回报数据(默认值)
        #   - 大于0, 以指定的回报编号为起点, 从该回报编号的下一条数据开始推送
        #   - 小于0, 从最新的数据开始推送回报数据
        rpt_channel2.lastInMsgSeq = -1
    # -------------------------


    # 5. 启动交易接口
    api.start()

    # 6. 等待处理结束
    # @note 提示:
    # - 只是出于演示的目的才如此处理, 实盘程序可以根据需要自行实现
    while not api.is_channel_connected(ord_channel1):
        print(">>> 正在等待委托通道1连接就绪... ")
        time.sleep(1)

    while not api.is_channel_connected(ord_channel2):
        print(">>> 正在等待委托通道2连接就绪... ")
        time.sleep(1)

    # @note 此处借用了 lastOutMsgSeq 字段来维护自增的 "客户委托流水号(clSeqNo)"
    api.set_last_cl_seq_no(
        last_cl_seq_no = max(ord_channel1.lastOutMsgSeq,
                             ord_channel2.lastOutMsgSeq)
    )

    # 7. 样例展示
    # - 委托接口使用样例
    order_sample(api)

    # - 撤单请求样例
    cancel_order_sample(api)

    # - 出入金请求样例
    fund_transfer_sample(api)

    # 8. (出于演示的目的) 基于委托通道2执行交易和查询
    assert api.get_channel_cfg(ord_channel1).channelTag \
           == api.get_channel_cfg(api.get_default_ord_channel()).channelTag
    assert api.get_channel_cfg(rpt_channel1).channelTag \
           == api.get_channel_cfg(api.get_default_rpt_channel()).channelTag

    # 8.1 委托通道2 - 查询资金信息
    api.query_cash_asset(channel=ord_channel2)

    # 8.2 委托通道2 - 发送委托请求信息 (上海A股市场的买卖)
    api.send_order(
        channel = ord_channel2,
        req=OesOrdReqT(
            clSeqNo=api.get_next_cl_seq_no(),
            mktId=eOesMarketIdT.OES_MKT_SH_ASHARE,
            ordType=eOesOrdTypeT.OES_ORD_TYPE_LMT,
            ordQty=1000,
            ordPrice=102800,
            securityId=b"600000",
            bsType=eOesBuySellTypeT.OES_BS_TYPE_BUY))


    # 9. 等待回报消息接收完成
    time.sleep(0.2)

    # 10. 释放资源
    api.release()


def oes_minimal_sample_main() -> None:
    """
    OES交易对接的样例代码 (精简版本)
    - 根据配置文件中的内容, 添加一个委托通道, 一个回报通道
    - 根据配置文件中的内容, 订阅回报数据
    """
    config_file_name: str = './oes_client_stk.conf'

    # 1. 创建交易API实例
    api: OesClientApi = OesClientApi(config_file_name)
    # 2. 创建自定义的SPI回调实例
    spi: OesClientMySpi = OesClientMySpi()

    # 3. 将SPI实例注册至API实例中, 以达到通过自定义的回调函数收取交易回报的效果
    if api.register_spi(spi, add_default_channel=True) is False:
        return

    """
    # 重置委托通道使用的用户名称和密码 (默认会使用配置文件中的设置)
    default_ord_channel = api.get_default_ord_channel()
    if default_ord_channel:
        # - username: 用户名
        # - password: 密码
        #   - 支持通过前缀指定密码类型, 如 md5:PASSWORD, txt:PASSWORD
        default_ord_channel.pChannelCfg.contents.remoteCfg.username = b"demo001"
        default_ord_channel.pChannelCfg.contents.remoteCfg.password = b"123456"
        
        # 在Start之前, 可以直接设置通道使用的环境号 (默认会使用配置文件中的设置)
        default_ord_channel.pChannelCfg.contents.remoteCfg.clEnvId = 1
    # -------------------------


    # 重置回报通道使用的用户名称和密码 (默认会使用配置文件中的设置)
    default_rpt_channel = api.get_default_rpt_channel()
    if default_rpt_channel:
        # - username: 用户名
        # - password: 密码
        #   - 支持通过前缀指定密码类型, 如 md5:PASSWORD, txt:PASSWORD
        default_rpt_channel.pChannelCfg.contents.remoteCfg.username = b"demo001"
        default_rpt_channel.pChannelCfg.contents.remoteCfg.password = b"123456"
        
        # 在Start之前, 可以直接设置通道使用的环境号 (默认会使用配置文件中的设置)
        api.get_channel_subscribe_cfg(default_rpt_channel).clEnvId = 2
        api.get_channel_subscribe_cfg(default_rpt_channel).rptTypes = 0
        
        # - lastInMsgSeq: 指定待订阅的回报数据的起始位置
        #   - 等于0, 从头开始推送回报数据(默认值)
        #   - 大于0, 以指定的回报编号为起点, 从该回报编号的下一条数据开始推送
        #   - 小于0, 从最新的数据开始推送回报数据
        default_rpt_channel.lastInMsgSeq = -1
    # -------------------------

    # 设置客户端自定义的IP地址、MAC地址
    # @note IP和MAC地址在登录时会尝试自动获取, 自动获取失败时会使用自定义设置
    # api.set_customized_ip_and_mac("192.168.0.1", "11:11:11:11:11:11")
    # -------------------------

    # 设置客户端本地的设备序列号
    # @note 设备序列号目前不会从自动获取, 需要主动设置以防止券商控制导致的登录失败, 同时满足监管需求
    # api.set_customized_driver_id("ABCDEFGHIJKLMN")
    # -------------------------

    # 设置客户端的交易终端软件名称
    # @note 设备序列号目前不会从自动获取, 需要主动设置以防止券商控制导致的登录失败, 同时满足监管需求
    # api.set_client_appl_name("quant360")
    # -------------------------

    # 设置客户端的交易终端软件版本
    # @note 设备序列号目前不会从自动获取, 需要主动设置以防止券商控制导致的登录失败, 同时满足监管需求
    # api.set_client_appl_version("v1.2.3")
    # -------------------------

    # 设置客户端的默认委托方式
    # @note 部分券商要求登录前填写委托方式, 如无此要求则无需调用该接口
    # api.set_default_entrust_way('K')
    # -------------------------
    """

    # 4. 启动交易API接口
    if api.start() is False:
        return

    # 5. 等待处理结束
    # @note 提示:
    # - 只是出于演示的目的才如此处理, 实盘程序可以根据需要自行实现
    while not api.is_channel_connected(api.get_default_ord_channel()):
        print(">>> 正在等待委托通道连接就绪... ")
        time.sleep(1)

    # @note 此处借用了 lastOutMsgSeq 字段来维护自增的 "客户委托流水号(clSeqNo)"
    api.set_last_cl_seq_no(
        last_cl_seq_no = api.get_default_ord_channel().lastOutMsgSeq
    )

    # 6. 样例展示
    # - 查询请求样例
    # query_sample(api)

    # - 委托接口使用样例
    order_sample(api)

    # - 撤单请求样例
    cancel_order_sample(api)

    # - 出入金请求样例
    fund_transfer_sample(api)

    # - 等待回报消息接收完成
    time.sleep(0.2)

    print("\n交易API运行结束, 即将退出! totalPicked[{}]\n".format(
        api.get_total_picked()))

    # 7. 释放资源
    api.release()

if __name__ == "__main__":
    # OES交易对接的样例代码 (精简版本)
    # - 根据配置文件中的内容, 添加一个委托通道, 一个回报通道
    # - 根据配置文件中的内容, 订阅回报数据
    oes_minimal_sample_main()

    # OES交易对接的样例代码
    # - 通过不同方式添加多个委托通道与多个回报通道, 每个回报通道订阅不同的回报信息
    #   - add_ord_channel_from_file
    #   - add_ord_channel
    #   - add_rpt_channel_from_file
    #   - add_rpt_channel
    # oes_sample_main()
