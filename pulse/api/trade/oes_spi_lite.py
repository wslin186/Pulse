# -*- coding: utf-8 -*-
"""
中文化的 OES SPI 回调实现——仅支持 A 股（深圳）市价/限价，正确实现所有抽象方法
"""
from datetime import datetime
from typing import Callable, Any

from vendor.trade_api import OesClientSpi
from vendor.trade_api.model import eOesBuySellTypeT, eOesOrdTypeSzT, eOesOrdTypeShT, OesFundTrsfReportT
from core.utils.logger import get_logger

log = get_logger("OesSpi")
_INT_MAX = 2**31 - 1

# 买卖类型中文映射
_SIDE_CN = {
    eOesBuySellTypeT.OES_BS_TYPE_BUY:  "买入",
    eOesBuySellTypeT.OES_BS_TYPE_SELL: "卖出"
}
# A 股委托类型中文映射（深圳+上海，含特殊"市价"方式）
_PRICE_TYPE_CN = {
    # 深圳
    eOesOrdTypeSzT.OES_ORD_TYPE_SZ_MTL_BEST:           "市价",
    eOesOrdTypeSzT.OES_ORD_TYPE_SZ_LMT:                "限价",
    # 上海市价/限价
    eOesOrdTypeShT.OES_ORD_TYPE_SH_MTL_BEST:           "市价",
    eOesOrdTypeShT.OES_ORD_TYPE_SH_LMT:                "限价",
}
# 状态码中文映射
_STATUS_CN = {8: "已成交", 5: "已拒绝", 6: "已撤单"}

def _now() -> str:
    return datetime.now().strftime("%H:%M:%S")

def _sym(b: Any) -> str:
    sid = getattr(b, "securityId", b"")
    return sid.decode() if isinstance(sid, (bytes, bytearray)) else str(sid)

class OesSpiLite(OesClientSpi):
    """专注于 A 股（深圳）委托回报/成交报告/资金/持仓，日志中文化"""
    __abstractmethods__ = set()

    def __init__(self, on_any: Callable[[Any], None] | None = None):
        super().__init__()
        self._hook = on_any
        # 记录 clSeqNo 对应的操作方向和委托类型
        self._side_map: dict[int, str] = {}
        self._price_type_map: dict[int, str] = {}

    def on_rpt_connect(self, channel: Any, user_info: Any) -> int:
        tag = channel.pChannelCfg.contents.channelTag.decode()
        log.info(f"[{_now()}] 回报通道[{tag}]已连接，开始订阅回报")
        self.oes_api.send_report_synchronization(
            channel, subscribe_env_id=0, subscribe_rpt_types=0, last_rpt_seq_num=_INT_MAX
        )
        return 0

    def on_ord_connect(self, channel: Any, user_info: Any) -> int:
        tag = channel.pChannelCfg.contents.channelTag.decode()
        log.info(f"[{_now()}] 委托通道[{tag}]已连接")
        return 0

    def on_order_insert(self, channel: Any, msg_head: Any, rpt_head: Any, rpt_body: Any, user_info: Any) -> int:
        # 委托生成回调，先于 on_order_report
        b = rpt_body
        if hasattr(b, 'clSeqNo') and hasattr(b, 'ordQty'):
            seq = b.clSeqNo
            bs = getattr(b, 'bsType', None)
            op = _SIDE_CN.get(bs, '')
            # 生成时也记录方向
            self._side_map[seq] = op
            log.info(f"[{_now()}] 委托生成 | 证券={_sym(b)} | 操作={op} | 数量={b.ordQty} | 单号={seq}")
        return 0

    def on_order_report(self, channel: Any, msg_head: Any, rpt_head: Any, rpt_body: Any, user_info: Any) -> int:
        # 订单回报：记录委托类型并输出中文
        b = rpt_body
        if hasattr(b, 'ordStatus'):
            seq = b.clSeqNo
            op = self._side_map.get(seq, '')
            ot = getattr(b, 'ordType', None)
            price_type = _PRICE_TYPE_CN.get(ot, '限价' if getattr(b, 'ordPrice', 0) else '市价')
            self._price_type_map[seq] = price_type
            qty = b.ordQty
            price_disp = '市价' if price_type == '市价' else f"{b.ordPrice/10000:.2f}"
            status = _STATUS_CN.get(b.ordStatus, f"状态{b.ordStatus}")
            log.info(
                f"[{_now()}] 订单回报 | 证券={_sym(b)} | 操作={op} | 数量={qty} | 类型={price_type}({price_disp}) | 单号={seq} | {status}"
            )
            if self._hook:
                self._hook(b)
        return 0

    def on_trade_report(self, channel: Any, msg_head: Any, rpt_head: Any, rpt_body: Any, user_info: Any) -> int:
        # 成交报告：沿用原委托类型
        b = rpt_body
        if hasattr(b, 'trdQty'):
            seq = b.clSeqNo
            op = self._side_map.get(seq, '')
            price_type = self._price_type_map.get(seq, '市价')
            price = b.trdPrice / 10000
            amt = b.trdAmt / 10000
            log.info(
                f"[{_now()}] 成交报告 | 证券={_sym(b)} | 操作={op} | 数量={b.trdQty} | 价格={price:.2f} ({price_type}) | 金额={amt:.2f} | 单号={seq}"
            )
            if self._hook:
                self._hook(b)
        return 0

    def on_cash_asset_variation(self, channel: Any, msg_head: Any, rpt_head: Any, rpt_body: Any, user_info: Any) -> int:
        b = rpt_body
        if hasattr(b, 'cashAvl') or hasattr(b, 'currentAvailableBal'):
            avail = getattr(b, 'currentAvailableBal', getattr(b, 'cashAvl', 0)) / 10000
            bal   = getattr(b, 'currentTotalBal', getattr(b, 'cashBal', 0)) / 10000
            log.info(f"[{_now()}] 资金变动 | 可用={avail:,.2f} | 余额={bal:,.2f}")
            if self._hook:
                self._hook(b)
        return 0

    def on_stock_holding_variation(self, channel: Any, msg_head: Any, rpt_head: Any, rpt_body: Any, user_info: Any) -> int:
        b = rpt_body
        if hasattr(b, 'sumHld') or hasattr(b, 'positionQty'):
            total = getattr(b, 'sumHld', getattr(b, 'positionQty', 0))
            sell  = getattr(b, 'sellAvlHld', getattr(b, 'sellAvlQty', 0))
            log.info(f"[{_now()}] 持仓变动 | 证券={_sym(b)} | 总={total} | 可卖={sell}")
            if self._hook:
                self._hook(b)
        return 0

    def on_rpt_disconnect(self, channel: Any, user_info: Any) -> int:
        log.warning(f"[{_now()}] ⚠️ 回报通道已断开")
        return 0

    def on_ord_disconnect(self, channel: Any, user_info: Any) -> int:
        log.warning(f"[{_now()}] ⚠️ 委托通道已断开")
        return 0

    def on_order_reject(self, channel, msg_head, rpt_head, rpt_body, user_info):
        seq = getattr(rpt_body, 'clSeqNo', None)
        reason = getattr(rpt_body, 'ordRejReason', getattr(rpt_body, 'rejReason', 0))
        log.error(f"[{_now()}] ❌ 订单被拒 | 单号={seq} | 原因代码={reason}")
        if self._hook:
            self._hook(rpt_body)
        return 0

    def on_fund_trsf_report(self, channel, msg_head, rpt_head, rpt_body: OesFundTrsfReportT, user_info):
        amt = getattr(rpt_body, 'trsfAmt', 0) / 10000
        status = getattr(rpt_body, 'trsfStatus', 0)
        log.info(f"[{_now()}] 出入金回报 | 金额={amt:,.2f} | 状态={status}")
        if self._hook:
            self._hook(rpt_body)
        return 0

    def on_report_synchronization(self, channel, msg_head, rpt_head, rpt_body, user_info):
        log.info(f"[{_now()}] ✅ 回报同步完成 seq={getattr(rpt_body, 'lastRptSeqNum', '')}")
        if self._hook:
            self._hook(rpt_body)
        return 0
