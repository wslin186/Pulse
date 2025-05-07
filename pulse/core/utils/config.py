from __future__ import annotations
from pathlib import Path
import yaml
from typing import Any

_BASE = Path(__file__).resolve().parents[3]      # 项目根

def load_yaml(path: str | Path) -> dict[str, Any]:
    real = Path(path) if Path(path).is_absolute() else _BASE / path
    with real.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_path(rel: str | Path) -> Path:
    """获取项目内相对文件路径"""
    return _BASE / rel
