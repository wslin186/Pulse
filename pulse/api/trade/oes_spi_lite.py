# -*- coding: utf-8 -*-
"""简化且稳健的 OES SPI —— 纯 f‑string 写法"""

from datetime import datetime
from typing import Callable, Any

from vendor.trade_api import OesClientSpi
from core.utils.logger import get_logger

log = get_logger("OesSpi")

_COL = {"sym": 8, "qty": 8, "px": 9, "clsq": 6}
FMT = "{sym:<{sym_w}}{qty:>{qty_w}}{px:>{px_w}.2f}{clsq:>{clsq_w}}".format
FMT_KW = dict(sym_w=_COL["sym"], qty_w=_COL["qty"],
              px_w=_COL["px"], clsq_w=_COL["clsq"])

_FILLED, _REJECT = 8, 5        # 请替换成官方枚举


def _now() -> str:
    return datetime.now().strftime("%H:%M:%S")


def _body(*args):
    for o in reversed(args):
        if hasattr(o, "securityId") or hasattr(o, "cashAcctId"):
            return o
    return None


def _sym(b) -> str:
    s = getattr(b, "securityId", b"")
    return s.decode() if isinstance(s, (bytes, bytearray)) else str(s)


def _to_px(x):                 # 价格从 INT(1/10000 元) 转回 float
    return x / 10000 if isinstance(x, int) else x


class OesSpiLite(OesClientSpi):
    """只关心 委托 / 成交 / 资金 / 持仓"""

    def __init__(self, on_any: Callable[[Any], None] | None = None):
        super().__init__()
        self._hook = on_any

        # ------- 回报通道连接成功 -------
    def on_rpt_connect(self, channel, user_info):
        """
        1. 打印一下日志（可选）
        2. 调用 OES 默认订阅逻辑
        """
        tag = channel.pChannelCfg.contents.channelTag.decode()
        log.info("📡 回报通道 [%s] 已连接，发送订阅指令…", tag)

        # 直接沿用配置文件 (clEnvId / rptTypes) 里的设置
        return self.oes_api.default_on_connect(channel)

    # ------------------  委托已生成  ------------------
    def on_order_insert(self, *a):
        b = _body(*a)
        if b:
            msg = ("📝({}) 委托 | ".format(_now()) +
                   FMT(sym=_sym(b), qty=b.ordQty,
                       px=_to_px(b.ordPrice), clsq=b.clSeqNo, **FMT_KW))
            log.info(msg)
            self._hook and self._hook(b)
        return 0

    # ------------------  委托回报  ------------------
    def on_order_report(self, *a):
        b = _body(*a)
        if b:
            flag = ("📩回报" if b.ordStatus == _FILLED
                    else "❌拒绝" if b.ordStatus == _REJECT
                    else "⌛状态")
            msg = (f"{flag} | " +
                   FMT(sym=_sym(b), qty=b.ordQty,
                       px=_to_px(b.ordPrice), clsq=b.clSeqNo, **FMT_KW) +
                   f" | 状态={b.ordStatus}")
            log.info(msg)
            self._hook and self._hook(b)
        return 0

    # ------------------  成交回报  ------------------
    def on_trade_report(self, *a):
        b = _body(*a)
        if b:
            msg = ("💥成交 | " +
                   FMT(sym=_sym(b), qty=b.trdQty,
                       px=_to_px(b.trdPrice), clsq=b.clSeqNo, **FMT_KW) +
                   f" | 金额={b.trdAmt / 10000:8.2f}")
            log.info(msg)
            self._hook and self._hook(b)
        return 0

    # ------------------  资金变动  ------------------
    def on_cash_asset_variation(self, *a):
        b = _body(*a)
        if b:
            avail = getattr(b, "currentAvailableBal",
                            getattr(b, "cashAvl", 0)) / 10000
            bal = getattr(b, "currentTotalBal",
                          getattr(b, "cashBal", 0)) / 10000
            log.info(f"💰资金 | 可用={avail:,.2f} | 余额={bal:,.2f}")
            self._hook and self._hook(b)
        return 0

    # ------------------  持仓变动  ------------------
    def on_stock_holding_variation(self, *a):
        b = _body(*a)
        if b:
            total = getattr(b, "sumHld", getattr(b, "positionQty", 0))
            sell = getattr(b, "sellAvlHld", getattr(b, "sellAvlQty", 0))
            log.info(f"📦持仓 | {_sym(b):<8} | 总={total:8d} | 可卖={sell:8d}")
            self._hook and self._hook(b)
        return 0

    # ---------- 断线告警 ----------
    def on_rpt_disconnect(self, *_): log.warning("⚠️  回报通道断开！"); return 0
    def on_ord_disconnect(self, *_): log.warning("⚠️  委托通道断开！"); return 0
