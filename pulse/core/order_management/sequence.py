# core/order_management/sequence.py
# -*- coding: utf-8 -*-
"""
clseqno_manager.py —— 线程安全的 clSeqNo 生成器
--------------------------------------------
• 初始值 = 默认委托通道的 lastOutMsgSeq + 1
• 每调 get_next_seq() 自动自增，并保持与 API 同步
• 提供 get_last_seq() 读取上一次发送的序号，供撤单时使用
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
        self._api = api
        self._lock = threading.Lock()

        if start is not None:
            self._seq = int(start)
        else:
            ch = api.get_default_ord_channel()
            last = getattr(ch, "lastOutMsgSeq", 0) if ch else 0
            self._seq = last + 1

        # 保存上一次发出的序号
        self._last_sent: Optional[int] = None

        # 同步到 C API 内部计数（方便重连等场景）
        self._api.set_last_cl_seq_no(self._seq)

    def get_next_seq(self) -> int:
        """
        返回一个新的 clSeqNo，并推进到下一个，同时同步给 C API。
        """
        with self._lock:
            seq = self._seq
            self._seq += 1
            # 记录本次发出的序号
            self._last_sent = seq
            # 同步到底层
            self._api.set_last_cl_seq_no(self._seq)
            return seq

    def get_last_seq(self) -> Optional[int]:
        """
        返回上一次通过 get_next_seq() 获取并发送的 clSeqNo。
        如果还没发过单，则返回 None。
        """
        return self._last_sent
