# -*- coding: utf-8 -*-
"""
交易api使用样例 (期权业务)
"""
import sys
import time

sys.path.append('../')

"""
@note 请从 trade_api 中引入交易API相关的结构体, 否则兼容性将无法得到保证
"""
from trade_api import (
    # spk_util.py

    # oes_base_constants.py
    eOesBuySellTypeT, eOesMarketIdT, eOesOrdTypeT,
    eOesOptPositionTypeT, eOesOrdTypeShOptT,

    # oes_base_model_credit.py
    # oes_base_model_option_.py

    # oes_base_model.py
    OesOrdReqT, OesOrdCancelReqT, OesOrdCnfmT,

    # oes_qry_packets.py
    OesClientOverviewT, OesCustOverviewT, OesCashAcctOverviewT,
    OesInvAcctOverviewT, OesQryCashAssetFilterT,

    # oes_qry_packets_credit.py
    # oes_qry_packets_option.py
    OesQryOptHoldingFilterT, OesQryOptPositionLimitFilterT,
    OesQryOptPurchaseLimitFilterT, OesQryOptUnderlyingHoldingFilterT,
    OesQryOptionFilterT,

    # oes_packets.py
    OesOptSettlementConfirmReqT,

    # oes_api.py
    OesClientApi,
)

from my_spi import (
    OesClientMySpi
)


# 上海期权合约代码
SH_OPT_SECURITY_ID: bytes = b"10001229"

# 上海期权合约代码对应的标的证券代码
SH_OPT_UNDERLYING_SECURITY_ID: bytes = b"510050"


def query_client_overview(api: OesClientApi) -> None:
    """
    查询客户端总览信息

    Args:
        api (OesClientApi): [oes-api客户端]
    """
    overview: OesClientOverviewT = api.get_client_overview()
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
              f"客户姓名[{cust_item.custName.decode()}]")

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
                  f"股东账户代码[{inv_acct.invAcctId.decode()}], "
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
                  f"股东账户代码[{inv_acct.invAcctId.decode()}], "
                  f"市场代码[{inv_acct.mktId}], 账户状态[{inv_acct.status}], "
                  f"是否禁止交易[{inv_acct.isTradeDisabled}], "
                  f"席位号[{inv_acct.pbuId}], "
                  f"当日累计有效交易类委托笔数[{inv_acct.trdOrdCnt}], "
                  f"当日累计有效非交易类委托笔数[{inv_acct.nonTrdOrdCnt}], "
                  f"当日累计有效撤单笔数[{inv_acct.cancelOrdCnt}], "
                  f"当日累计被OES拒绝的委托笔数[{inv_acct.oesRejectOrdCnt}], "
                  f"当日累计被交易所拒绝的委托笔数[{inv_acct.exchRejectOrdCnt}], "
                  f"当日累计成交笔数[{inv_acct.trdCnt}]")


def query_sample(api: OesClientApi) -> None:
    """
    查询接口使用样例
    - @note 批量查询到的总条数为0时, 不会触发回调函数 (对应my_spi.py中的函数)

    Args:
        api (OesClientApi): [oes-api客户端]
    """

    """ 查询 客户端总览信息 """
    query_client_overview(api)


    """ 查询期权结算单 """
    statement: str = api.get_opt_settlement_statement()
    print(statement)


    """ 查询 所有关联资金账户的资金信息 """
    api.query_cash_asset()


    """ 查询 指定资金账户的资金信息 """
    api.query_cash_asset(
        qry_filter=OesQryCashAssetFilterT(cashAcctId=b"******"))


    """ 查询 通知消息 """
    api.query_notify_info()


    """ 查询期权标的持仓 """
    api.query_opt_underlying_holding(
        qry_filter=OesQryOptUnderlyingHoldingFilterT(
            mktId=eOesMarketIdT.OES_MKT_UNDEFINE))


    """ 查询期权限仓额度 """
    api.query_opt_position_limit(
        qry_filter=OesQryOptPositionLimitFilterT(
            mktId=eOesMarketIdT.OES_MKT_UNDEFINE))


    """ 查询期权限购额度 """
    api.query_opt_purchase_limit(
        qry_filter=OesQryOptPurchaseLimitFilterT(
            mktId=eOesMarketIdT.OES_MKT_UNDEFINE))


    """ 查询 上海期权市场 指定期权产品(SH_OPT_SECURITY_ID) 的产品信息 """
    api.query_option(
        qry_filter=OesQryOptionFilterT(
            securityId=SH_OPT_SECURITY_ID,
            mktId=eOesMarketIdT.OES_MKT_UNDEFINE))


    """ 查询 上海期权市场 全部 的产品信息 """
    api.query_option(
        qry_filter=OesQryOptionFilterT(mktId=eOesMarketIdT.OES_MKT_SH_OPTION))


    """ 查询 上海期权市场 指定期权产品(SH_OPT_SECURITY_ID) 的权利仓持仓 """
    api.query_opt_holding(
        qry_filter=OesQryOptHoldingFilterT(
            positionType=eOesOptPositionTypeT.OES_OPT_POSITION_TYPE_LONG,
            securityId=SH_OPT_SECURITY_ID,
            mktId=eOesMarketIdT.OES_MKT_SH_OPTION))


    """ 查询 上海期权市场 指定期权产品(SH_OPT_SECURITY_ID) 的所有持仓 """
    api.query_opt_holding(
        qry_filter=OesQryOptHoldingFilterT(
            positionType=eOesOptPositionTypeT.OES_OPT_POSITION_TYPE_UNDEFINE,
            securityId=SH_OPT_SECURITY_ID,
            mktId=eOesMarketIdT.OES_MKT_SH_OPTION))


    """ 查询 上海期权市场的所有持仓 """
    api.query_opt_holding(
        qry_filter=OesQryOptHoldingFilterT(
            positionType=eOesOptPositionTypeT.OES_OPT_POSITION_TYPE_UNDEFINE,
            mktId=eOesMarketIdT.OES_MKT_SH_OPTION))


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

    # 期权结算单确认
    #  - 期权客户结算单确认后, 方可进行委托申报和出入金请求
    #  - 期权结算单只需确认一次, 不需要重复确认 (重复确认时函数返回值为成功 0)
    #  - 客户端仅关联一个客户时, 可不指定客户代码; 否则需指定待确认的客户代码

    ret: int = api.send_opt_settlement_confirm(
        req=OesOptSettlementConfirmReqT())
    if ret != 0:
        # 结算单确认失败时直接退出
        print(f"期权结算单确认失败, 退出程序! err_code[{ret}], "
              f"err_msg[{api.get_error_msg(ret)}]")
        api.release()
        sys.exit(-1)


    # 上海期权市场的买开
    # - 以 0.5元 买开 指定期权产品(SH_OPT_SECURITY_ID) 1张
    # - 此处需自行配置交易的期权合约代码和对应的价格
    ret = api.send_order(
        req=OesOrdReqT(
            clSeqNo=api.get_next_cl_seq_no(),
            mktId=eOesMarketIdT.OES_MKT_SH_OPTION,
            securityId=SH_OPT_SECURITY_ID,
            bsType=eOesBuySellTypeT.OES_BS_TYPE_BUY_OPEN,
            ordType=eOesOrdTypeT.OES_ORD_TYPE_LMT,
            ordPrice=5000,
            ordQty=1))
    if ret < 0:
        print("发送委托请求失败, 参数错误? 请参考日志信息检查相关数据是否合法!")
        return


    # 上海期权市场的卖平
    # - 以 市价 卖平 指定期权产品(SH_OPT_SECURITY_ID) 1张
    ret = api.send_order(
        req=OesOrdReqT(
            clSeqNo=api.get_next_cl_seq_no(),
            mktId=eOesMarketIdT.OES_MKT_SH_OPTION,
            securityId=SH_OPT_SECURITY_ID,
            bsType=eOesBuySellTypeT.OES_BS_TYPE_SELL_CLOSE,
            ordType=eOesOrdTypeShOptT.OES_ORD_TYPE_SHOPT_FOK,
            ordQty=1))
    if ret < 0:
        print("发送委托请求失败, 参数错误? 请参考日志信息检查相关数据是否合法!")
        return


    # 上海期权市场的标的锁定
    # - 锁定 期权产品(SH_OPT_SECURITY_ID)
    # 对应的标的证券(SH_OPT_UNDERLYING_SECURITY_ID) 10000 股
    ret = api.send_order(
        req=OesOrdReqT(
            clSeqNo=api.get_next_cl_seq_no(),
            mktId=eOesMarketIdT.OES_MKT_SH_OPTION,
            securityId=SH_OPT_UNDERLYING_SECURITY_ID,
            bsType=eOesBuySellTypeT.OES_BS_TYPE_UNDERLYING_FREEZE,
            ordType=eOesOrdTypeT.OES_ORD_TYPE_LMT,
            ordQty=10000))
    if ret < 0:
        print("发送委托请求失败, 参数错误? 请参考日志信息检查相关数据是否合法!")
        return


    # 上海期权市场的备兑开仓
    # - 以 市价 备兑开仓 指定期权产品(SH_OPT_SECURITY_ID) 1张
    ret = api.send_order(
        req=OesOrdReqT(
            clSeqNo=api.get_next_cl_seq_no(),
            mktId=eOesMarketIdT.OES_MKT_SH_OPTION,
            securityId=SH_OPT_SECURITY_ID,
            bsType=eOesBuySellTypeT.OES_BS_TYPE_COVERED_OPEN,
            ordType=eOesOrdTypeShOptT.OES_ORD_TYPE_SHOPT_FOK,
            ordQty=1))
    if ret < 0:
        print("发送委托请求失败, 参数错误? 请参考日志信息检查相关数据是否合法!")
        return


    # 上海期权市场的备兑平仓
    # - 以 市价 备兑平仓 指定期权产品(SH_OPT_SECURITY_ID) 1张
    ret = api.send_order(
        req=OesOrdReqT(
            clSeqNo=api.get_next_cl_seq_no(),
            mktId=eOesMarketIdT.OES_MKT_SH_OPTION,
            securityId=SH_OPT_SECURITY_ID,
            bsType=eOesBuySellTypeT.OES_BS_TYPE_COVERED_CLOSE,
            ordType=eOesOrdTypeShOptT.OES_ORD_TYPE_SHOPT_FOK,
            ordQty=1))
    if ret < 0:
        print("发送委托请求失败, 参数错误? 请参考日志信息检查相关数据是否合法!")
        return


    # 上海期权市场的标的解锁
    # - 解锁 期权产品(SH_OPT_SECURITY_ID)
    # 对应的的标的证券(SH_OPT_UNDERLYING_SECURITY_ID) 10000 股
    ret = api.send_order(
        req=OesOrdReqT(
            clSeqNo=api.get_next_cl_seq_no(),
            mktId=eOesMarketIdT.OES_MKT_SH_OPTION,
            securityId=SH_OPT_UNDERLYING_SECURITY_ID,
            bsType=eOesBuySellTypeT.OES_BS_TYPE_UNDERLYING_UNFREEZE,
            ordType=eOesOrdTypeT.OES_ORD_TYPE_LMT,
            ordQty=10000))
    if ret < 0:
        print("发送委托请求失败, 参数错误? 请参考日志信息检查相关数据是否合法!")
        return


    # 上海期权市场的期权行权
    # - 行权 指定期权产品(SH_OPT_SECURITY_ID) 1 张
    ret = api.send_order(
        req=OesOrdReqT(
            clSeqNo=api.get_next_cl_seq_no(),
            mktId=eOesMarketIdT.OES_MKT_SH_OPTION,
            securityId=SH_OPT_SECURITY_ID,
            bsType=eOesBuySellTypeT.OES_BS_TYPE_OPTION_EXERCISE,
            ordType=eOesOrdTypeT.OES_ORD_TYPE_LMT,
            ordQty=1))
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
        mktId=eOesMarketIdT.OES_MKT_SH_OPTION,
        clEnvId=1,
        clSeqNo=11,
        clOrdId=111,
    )


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


def oes_opt_sample_main() -> None:
    """
    OES交易对接的样例代码 (期权业务)
    - 根据配置文件中的内容, 添加一个委托通道, 一个回报通道
    - 根据配置文件中的内容, 订阅回报数据
    """
    config_file_name: str = './oes_client_opt.conf'

    # 1. 创建交易API实例
    api: OesClientApi = OesClientApi(config_file_name)
    # 2. 创建自定义的SPI回调实例
    spi: OesClientMySpi = OesClientMySpi()

    # 3. 将SPI实例注册至API实例中, 以达到通过自定义的回调函数收取交易回报的效果
    if api.register_spi(spi, add_default_channel=True) is False:
        return

    """
    # 设置客户端自定义的IP地址、MAC地址
    # @note IP和MAC地址在登录时会尝试自动获取, 自动获取失败时会使用自定义设置
    # api.set_customized_ip_and_mac("192.168.0.1", "11:11:11:11:11:11")
    # -------------------------

    # 设置客户端本地的设备序列号
    # @note 设备序列号目前不会从自动获取, 需要主动设置以防止券商控制导致的登录失败, 同时满足监管需求
    # api.set_customized_driver_id("ABCDEFGHIJKLMN")
    # -------------------------

    # 设置客户端的默认委托方式
    # @note 部分券商要求登录前填写委托方式, 如无此要求则无需调用该接口
    # api.set_default_entrust_way('K')
    # -------------------------
    """

    # 4. 启动交易API接口
    api.start()

    # 5. 等待处理结束
    # @note 提示:
    # - 只是出于演示的目的才如此处理, 实盘程序可以根据需要自行实现
    while not api.is_channel_connected(api.get_default_channel()):
        print(">>> 正在等待委托通道连接就绪... ")
        time.sleep(1)

    # @note 此处借用了 lastOutMsgSeq 字段来维护自增的 "客户委托流水号(clSeqNo)"
    api.set_last_cl_seq_no(
        last_cl_seq_no = api.get_default_ord_channel().lastOutMsgSeq
    )

    # 6. 样例展示
    # - 查询请求样例
    query_sample(api)

    # - 委托请求样例
    order_sample(api)

    # - 撤单请求样例
    cancel_order_sample(api)

    # - 等待回报消息接收完成
    time.sleep(0.2)

    # 7. 释放资源
    api.release()


if __name__ == "__main__":
    # OES交易对接的样例代码 (期权业务)
    # - 根据配置文件中的内容, 添加一个委托通道, 一个回报通道
    # - 根据配置文件中的内容, 订阅回报数据
    oes_opt_sample_main()
