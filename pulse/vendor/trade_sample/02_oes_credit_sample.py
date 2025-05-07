# -*- coding: utf-8 -*-
"""
交易api使用样例 (融资融券业务)
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
    eOesBuySellTypeT, eOesMarketIdT,
    eOesOrdTypeT, eOesOrdTypeSzT, eOesOrdTypeShT,
    eOesCrdAssignableRepayModeT, eOesCrdCashGroupPropertyT,

    # oes_base_model_credit.py
    # oes_base_model_option_.py
    # oes_base_model.py
    OesOrdReqT, OesOrdCancelReqT, OesOrdCnfmT,

    # oes_qry_packets.py
    OesClientOverviewT, OesCustOverviewT,
    OesCashAcctOverviewT, OesInvAcctOverviewT,

    # oes_qry_packets_credit.py
    OesCrdCollateralTransferOutMaxQtyItemT, OesCrdDrawableBalanceItemT,
    OesQryCrdCashPositionFilterT, OesQryCrdSecurityPositionFilterT,

    # oes_qry_packets_option.py
    # oes_packets.py

    # oes_api.py
    OesClientApi,
)

from my_spi import (
    OesClientMySpi
)


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
          f"客户端名称[{overview.clientName}], "
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
        print(f"    >>> 客户总览信息: 客户代码[{cust_item.custId}], "
              f"客户状态[{cust_item.status}], 风险评级[{cust_item.riskLevel}], "
              f"营业部代码[{cust_item.branchId}], 客户姓名[{cust_item.custName}]")

        cash_acct: OesCashAcctOverviewT = cust_item.cashAcct
        if cash_acct.isValid:
            print(
                f"        >>> 资金账户总览: 资金账户[{cash_acct.cashAcctId}], "
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
            print(f"        >>> 股东账户总览: 股东账户代码[{inv_acct.invAcctId}], "
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

def query_sample(api: OesClientApi) -> None:
    """
    查询接口使用样例
    - @note 批量查询到的总条数为0时, 不会触发回调函数 (对应my_spi.py中的函数)

    Args:
        api (OesClientApi): [oes-api客户端]
    """

    """ 查询 客户端总览信息 """
    query_client_overview(api)


    """ 查询 所有关联资金账户的资金信息 """
    api.query_cash_asset()


    """ 查询 信用资产信息 """
    api.query_crd_credit_asset()


    """ 查询 通知消息 """
    api.query_notify_info()


    """ 查询 沪深两市 融资融券合约信息 """
    api.query_crd_debt_contract()


    """ 查询 沪深两市 客户单证券融资融券负债统计信息 """
    api.query_crd_security_debt_stats()


    """ 查询 沪深两市 融资融券业务公共资金头寸信息（可融资头寸） """
    api.query_crd_cash_position(
        qry_filter=OesQryCrdCashPositionFilterT(
            cashGroupProperty=eOesCrdCashGroupPropertyT.
                OES_CRD_CASH_GROUP_PROP_PUBLIC))


    """ 查询 沪深两市 融资融券业务专项证券头寸信息 (可融券头寸) """
    api.query_crd_security_position(
        qry_filter=OesQryCrdSecurityPositionFilterT(
            cashGroupProperty=eOesCrdCashGroupPropertyT.
                OES_CRD_CASH_GROUP_PROP_SPECIAL))


    """ 查询 融资融券最大可取资金 """
    balance: OesCrdDrawableBalanceItemT = api.get_crd_drawable_balance()
    print(f">>> 查询到融资融券最大可取资金: "
          f"客户代码[{balance.custId}], "
          f"资金账户代码[{balance.cashAcctId}], "
          f"可取资金[{balance.drawableBal}]")


    """ 查询 融资融券担保品可转出的最大数 """
    max_qty: OesCrdCollateralTransferOutMaxQtyItemT = \
        api.get_crd_collateral_transfer_out_max_qty(
            security_id="600000", mkt_id=eOesMarketIdT.OES_MKT_UNDEFINE)
    print(f">>> 查询到融资融券担保品可转出的最大数: "
          f"客户代码[{max_qty.custId}], "
          f"证券代码[{max_qty.securityId}], "
          f"市场代码[{max_qty.mktId}], "
          f"融资融券担保品可转出的最大数量"
          f"[{max_qty.collateralTransferOutMaxQty}]")


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

    # 深圳A股的担保品划转
    # - 从普通账户 转入 平安银行(000001) 200股 到信用账户作为担保品
    ret = api.send_order(
        req=OesOrdReqT(
            clSeqNo=api.get_next_cl_seq_no(),
            mktId=eOesMarketIdT.OES_MKT_SZ_ASHARE,
            securityId=b"000001",
            ordType=eOesOrdTypeT.OES_ORD_TYPE_LMT,
            bsType=eOesBuySellTypeT.OES_BS_TYPE_COLLATERAL_TRANSFER_IN,
            ordQty=200,
            ordPrice=0))
    if ret < 0:
        print("发送委托请求失败, 参数错误? 请参考日志信息检查相关数据是否合法!")
        return


    # 深圳A股的担保品划转
    # - 从信用账户 转出 平安银行(000001) 100股担保品 到普通账户
    ret = api.send_order(
        req=OesOrdReqT(
            clSeqNo=api.get_next_cl_seq_no(),
            mktId=eOesMarketIdT.OES_MKT_SZ_ASHARE,
            securityId=b"000001",
            ordType=eOesOrdTypeT.OES_ORD_TYPE_LMT,
            bsType=eOesBuySellTypeT.OES_BS_TYPE_COLLATERAL_TRANSFER_OUT,
            ordQty=100,
            ordPrice=0))
    if ret < 0:
        print("发送委托请求失败, 参数错误? 请参考日志信息检查相关数据是否合法!")
        return


    # 上海A股的担保品买卖
    # - 以 11.85元 购入 浦发银行(600000) 100股 作为信用交易担保品
    ret = api.send_order(
        req=OesOrdReqT(
            clSeqNo=api.get_next_cl_seq_no(),
            mktId=eOesMarketIdT.OES_MKT_SH_ASHARE,
            securityId=b"600000",
            ordType=eOesOrdTypeT.OES_ORD_TYPE_LMT,
            bsType=eOesBuySellTypeT.OES_BS_TYPE_COLLATERAL_BUY,
            ordQty=100,
            ordPrice=118500))
    if ret < 0:
        print("发送委托请求失败, 参数错误? 请参考日志信息检查相关数据是否合法!")
        return


    # 深圳A股的担保品买卖
    # - 以 市价(最优五档即时成交剩余转限价委托) 卖出 万科A(000002) 100股 担保品
    ret = api.send_order(
        req=OesOrdReqT(
            clSeqNo=api.get_next_cl_seq_no(),
            mktId=eOesMarketIdT.OES_MKT_SZ_ASHARE,
            securityId=b"000002",
            ordType=eOesOrdTypeSzT.OES_ORD_TYPE_SZ_FOK,
            bsType=eOesBuySellTypeT.OES_BS_TYPE_COLLATERAL_SELL,
            ordQty=100,
            ordPrice=0))
    if ret < 0:
        print("发送委托请求失败, 参数错误? 请参考日志信息检查相关数据是否合法!")
        return


    # 上海A股融资买入
    # - 以 市价(最优五档即时成交剩余撤销委托) 融资买入 浦发银行(600000) 300股
    ret = api.send_order(
        req=OesOrdReqT(
            clSeqNo=api.get_next_cl_seq_no(),
            mktId=eOesMarketIdT.OES_MKT_SH_ASHARE,
            securityId=b"600000",
            ordType=eOesOrdTypeShT.OES_ORD_TYPE_SH_FAK_BEST_5,
            bsType=eOesBuySellTypeT.OES_BS_TYPE_MARGIN_BUY,
            ordQty=300,
            ordPrice=0))
    if ret < 0:
        print("发送委托请求失败, 参数错误? 请参考日志信息检查相关数据是否合法!")
        return


    # 直接还款
    # - 指定合约编号 以现金方式 直接还款 1.0000元
    ret = api.send_credit_cash_repay_req(
        cl_seq_no=api.get_next_cl_seq_no(),
        repay_amt=10000,
        repay_mode=eOesCrdAssignableRepayModeT.OES_CRD_ASSIGNABLE_REPAY_MODE_DEFAULT,
        debt_id="2018020100520000100056")
    if ret < 0:
        print("发送委托请求失败, 参数错误? 请参考日志信息检查相关数据是否合法!")
        return


    # 卖券还款
    # - 以 市价(对手方最优价格委托) 卖出 万科A(000002) 100股 偿还融资负债
    ret = api.send_credit_repay_req(
        req=OesOrdReqT(
            clSeqNo=api.get_next_cl_seq_no(),
            mktId=eOesMarketIdT.OES_MKT_SZ_ASHARE,
            securityId=b"000002",
            ordType=eOesOrdTypeSzT.OES_ORD_TYPE_SZ_MTL_BEST,
            bsType=eOesBuySellTypeT.OES_BS_TYPE_REPAY_MARGIN_BY_SELL,
            ordQty=100,
            ordPrice=0),
        repay_mode=eOesCrdAssignableRepayModeT.OES_CRD_ASSIGNABLE_REPAY_MODE_DEFAULT)
    if ret < 0:
        print("发送委托请求失败, 参数错误? 请参考日志信息检查相关数据是否合法!")
        return


    # 上海A股 融券卖出
    # - 融入 浦发银行(600000) 100股，并以限价 13.17元 卖出
    ret = api.send_order(
        req=OesOrdReqT(
            clSeqNo=api.get_next_cl_seq_no(),
            mktId=eOesMarketIdT.OES_MKT_SH_ASHARE,
            securityId=b"600000",
            ordType=eOesOrdTypeShT.OES_ORD_TYPE_SH_LMT,
            bsType=eOesBuySellTypeT.OES_BS_TYPE_SHORT_SELL,
            ordQty=100,
            ordPrice=131700))
    if ret < 0:
        print("发送委托请求失败, 参数错误? 请参考日志信息检查相关数据是否合法!")
        return


    # 上海A股 买券还券
    # - 以 限价13.10元 买入 浦发银行(600000) 100股 偿还融券负债
    # - 此处仅用于展示, 当日新开融券负债当日不能归还
    ret = api.send_credit_repay_req(
        req=OesOrdReqT(
            clSeqNo=api.get_next_cl_seq_no(),
            mktId=eOesMarketIdT.OES_MKT_SH_ASHARE,
            securityId=b"600000",
            ordType=eOesOrdTypeShT.OES_ORD_TYPE_SH_LMT,
            bsType=eOesBuySellTypeT.OES_BS_TYPE_REPAY_STOCK_BY_BUY,
            ordQty=100,
            ordPrice=131000),
        repay_mode=eOesCrdAssignableRepayModeT.OES_CRD_ASSIGNABLE_REPAY_MODE_DEFAULT)
    if ret < 0:
        print("发送委托请求失败, 参数错误? 请参考日志信息检查相关数据是否合法!")
        return


    # 直接还券
    #  - 直接归还 融资融券业务 浦发银行(600000) 100股融券信用负债
    #  - 此处仅用于展示, 当日新开融券负债当日不能归还
    ret = api.send_credit_repay_req(
        req=OesOrdReqT(
            clSeqNo=api.get_next_cl_seq_no(),
            mktId=eOesMarketIdT.OES_MKT_SH_ASHARE,
            securityId=b"600000",
            ordType=eOesOrdTypeShT.OES_ORD_TYPE_SH_MTL_BEST,
            bsType=eOesBuySellTypeT.OES_BS_TYPE_REPAY_STOCK_DIRECT,
            ordQty=100,
            ordPrice=0),
        repay_mode=eOesCrdAssignableRepayModeT.OES_CRD_ASSIGNABLE_REPAY_MODE_DEFAULT)
    if ret < 0:
        print("发送委托请求失败, 参数错误? 请参考日志信息检查相关数据是否合法!")
        return


    # 直接还款
    # - 以现金方式 仅归还息费 1.0000元 (此归还模式需券商支持)
    # - 仅归还息费模式下, 可以偿还包括融券合约在内的合约息费 (当日新开融券合约不允许当日归还)
    ret = api.send_credit_cash_repay_req(
        cl_seq_no=api.get_next_cl_seq_no(),
        repay_amt=10000,
        repay_mode=eOesCrdAssignableRepayModeT.OES_CRD_ASSIGNABLE_REPAY_MODE_INTEREST_ONLY)
    if ret < 0:
        print("发送委托请求失败, 参数错误? 请参考日志信息检查相关数据是否合法!")
        return


    # 卖券还款
    # - 以 市价(对手方最优价格委托) 卖出 万科A(000002) 100股 仅归还息费 (此归还模式需券商支持)
    # - 仅归还息费模式下, 可以偿还包括融券合约在内的合约息费 (当日新开融券合约不允许当日归还)
    ret = api.send_credit_repay_req(
        req=OesOrdReqT(
            clSeqNo=api.get_next_cl_seq_no(),
            mktId=eOesMarketIdT.OES_MKT_SZ_ASHARE,
            securityId=b"000002",
            ordType=eOesOrdTypeSzT.OES_ORD_TYPE_SZ_MTL_BEST,
            bsType=eOesBuySellTypeT.OES_BS_TYPE_REPAY_MARGIN_BY_SELL,
            ordQty=100,
            ordPrice=0),
        repay_mode=eOesCrdAssignableRepayModeT.OES_CRD_ASSIGNABLE_REPAY_MODE_INTEREST_ONLY)
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
        clOrdId=111,
    )

    # 通过待撤委托的 clOrdId 进行撤单
    ret = api.send_cancel_order(
        req=OesOrdCancelReqT(
            mktId=orig_order.mktId,
            origClOrdId=orig_order.clOrdId))
    if ret < 0:
        print("发送撤单委托请求失败, 参数错误? 请参考日志信息检查相关数据是否合法!")
        return


    # 通过待撤委托的 clSeqNo + clEnvId 进行撤单
    ret = api.send_cancel_order(
        req=OesOrdCancelReqT(
            mktId=orig_order.mktId,
            origClSeqNo=orig_order.clSeqNo,
            origClEnvId=orig_order.clEnvId))
    if ret < 0:
        print("发送撤单委托请求失败, 参数错误? 请参考日志信息检查相关数据是否合法!")
        return

def oes_crd_sample_main() -> None:
    """
    OES交易对接的样例代码 (融资融券业务)
    - 根据配置文件中的内容, 添加一个委托通道, 一个回报通道
    - 根据配置文件中的内容, 订阅回报数据
    """
    config_file_name: str = './oes_client_crd.conf'

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
    while not api.is_channel_connected(api.get_default_ord_channel()):
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
    # OES交易对接的样例代码 (融资融券业务)
    # - 根据配置文件中的内容, 添加一个委托通道, 一个回报通道
    # - 根据配置文件中的内容, 订阅回报数据
    oes_crd_sample_main()
