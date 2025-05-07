# -*- coding: utf-8 -*-
"""
统一日志工具：get_logger(name) → logging.Logger
"""
import logging
from logging import Logger
from pathlib import Path

_LOG_FMT = "%(asctime)s | %(name)-15s | %(levelname)-8s | %(message)s"
_LOG_DATE_FMT = "%Y-%m-%d %H:%M:%S"

def _ensure_root_handler() -> None:
    """项目启动时只初始化一次根 Handler，避免重复输出"""
    root = logging.getLogger()
    if root.handlers:               # 已经配置过
        return

    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(_LOG_FMT, _LOG_DATE_FMT))
    root.addHandler(console)
    root.setLevel(logging.INFO)

    # 可选：落地到文件
    log_dir = Path("./logs")
    log_dir.mkdir(exist_ok=True)
    file_handler = logging.FileHandler(log_dir / "pulse.log", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(_LOG_FMT, _LOG_DATE_FMT))
    root.addHandler(file_handler)

def get_logger(name: str) -> Logger:
    """获取带统一格式的 logger"""
    _ensure_root_handler()
    return logging.getLogger(name)
