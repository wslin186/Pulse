# -*- coding: utf-8 -*-
"""
订单发送 / 撤单 封装
-------------------------------------------------
全部使用 ClSeqNoManager 自动取号，不再手动传 clSeqNo
"""
from typing import Optional

from src.external_apis.trade_api.oes_api import (
    OesClientApi, OesOrdReqT, OesOrdCancelReqT
)
from src.external_apis.trade_api.model import (
    eOesBuySellTypeT,
    eOesOrdTypeShT,
    eOesOrdTypeSzT,
    eOesMarketIdT,
)
from src.order_management.clseqno_manager import ClSeqNoManager


# ---------------------------------------------------------------------- #
def send_order(
    api: OesClientApi,
    cl_seq_mgr: ClSeqNoManager,
    mkt: int,
    security_id: str,
    side: int,
    qty: int,
    price: Optional[float] = None,
) -> int:
    """
    下单接口

    参数
    ----
    api          : 已连接并启动的 OesClientApi
    cl_seq_mgr   : ClSeqNoManager 实例
    mkt          : eOesMarketIdT
    security_id  : 证券代码
    side         : eOesBuySellTypeT
    qty          : 数量（股/张）
    price        : 价格；深市可为空（走最优五档即成剩撤）
    """
    req = OesOrdReqT()
    req.clSeqNo = cl_seq_mgr.get_next_seq()
    req.mktId = mkt
    req.securityId = security_id.encode("utf-8")
    req.bsType = side
    req.ordQty = qty

    if mkt == eOesMarketIdT.OES_MKT_SH_ASHARE:
        if price is None:
            raise ValueError("上交所限价单必须填写价格")
        req.ordType = eOesOrdTypeShT.OES_ORD_TYPE_SH_LMT
        req.ordPrice = int(price * 10000)

    elif mkt == eOesMarketIdT.OES_MKT_SZ_ASHARE:
        if price is None:
            req.ordType = eOesOrdTypeSzT.OES_ORD_TYPE_SZ_MTL_BEST
        else:
            req.ordType = eOesOrdTypeSzT.OES_ORD_TYPE_SZ_LMT
            req.ordPrice = int(price * 10000)

    else:
        raise ValueError("❌不支持的市场类型")

    return api.send_order(api.get_default_ord_channel(), req)


# ---------------------------------------------------------------------- #
def cancel_order(
    api: OesClientApi,
    cl_seq_mgr: ClSeqNoManager,
    mkt: int,
    *,
    orig_cl_ord_id: Optional[int] = None,
    orig_cl_seq_no: Optional[int] = None,
    orig_cl_env_id: Optional[int] = None,
) -> int:
    """
    撤单接口

    任选：
      • orig_cl_ord_id
      • (orig_cl_seq_no + orig_cl_env_id)
    二选一
    """
    req = OesOrdCancelReqT()
    req.clSeqNo = cl_seq_mgr.get_next_seq()
    req.mktId = mkt

    if orig_cl_ord_id is not None:
        req.origClOrdId = orig_cl_ord_id
    elif orig_cl_seq_no is not None and orig_cl_env_id is not None:
        req.origClSeqNo = orig_cl_seq_no
        req.origClEnvId = orig_cl_env_id
    else:
        raise ValueError("⚠️撤单需提供 orig_cl_ord_id 或 (orig_cl_seq_no + orig_cl_env_id)")

    return api.send_cancel_order(api.get_default_ord_channel(), req)
