from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Order:
    id: int
    symbol: str
    side: str            # "BUY" / "SELL"
    qty: int
    price: float
    dt: datetime

@dataclass
class Fill:
    order_id: int
    symbol: str
    side: str
    qty: int
    price: float
    dt: datetime
