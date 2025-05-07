# -*- coding: utf-8 -*-
"""
clseqno_manager.py —— 线程安全的 clSeqNo 生成器
--------------------------------------------
• 初始值 = 默认委托通道的 lastOutMsgSeq + 1
• 每调 next() 自动自增，并保持与 API 同步
"""
from __future__ import annotations
import threading
from typing import Optional, Any

class ClSeqNoManager:
    def __init__(self, api: Any, start: Optional[int] = None) -> None:
        """
        Args:
            api  : 已经 login+start 的 OesClientApi
            start: 手动指定起始 clSeqNo；若 None 则用
                   api.get_default_ord_channel().lastOutMsgSeq + 1
        """
        self._api  = api
        self._lock = threading.Lock()

        if start is not None:
            self._seq = int(start)
        else:
            ch = api.get_default_ord_channel()
            last = getattr(ch, "lastOutMsgSeq", 0) if ch else 0
            self._seq = last + 1

        # 同步到 C API 内部计数（方便重连等场景）
        self._api.set_last_cl_seq_no(self._seq)

    # -----------------------------------------------------------
    def next(self) -> int:
        """返回一个新的 clSeqNo"""
        with self._lock:
            seq = self._seq
            self._seq += 1
            self._api.set_last_cl_seq_no(self._seq)
            return seq
