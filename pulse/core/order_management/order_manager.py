from vendor.trade_api import OesOrdReqT, eOesOrdTypeT

def send_order(api, cl_mgr,
               *, mkt, security_id: str,
               side, qty: int, price: float):
    """price: 元，内部自动 ×10000"""
    req = OesOrdReqT(
        clSeqNo=cl_mgr.next(),
        mktId=mkt,
        securityId=security_id.encode(),
        bsType=side,
        ordType=eOesOrdTypeT.OES_ORD_TYPE_LMT,
        ordQty=qty,
        ordPrice=int(price * 10000))
    return api.send_order(req=req)
