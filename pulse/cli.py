# pulse/cli.py

import argparse
import asyncio
from pathlib import Path

from pulse.core.utils.logger import get_logger
from pulse.core.utils.config import load_yaml
from pulse.core.data.market_data_provider import MarketDataProvider
from pulse.core.execution.broker import LiveBroker
from pulse.core.risk.risk_manager import RiskManager
from pulse.core.strategy.base_strategy import BaseStrategy

_LOG = get_logger("CLI")

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser("Pulse Quant Framework")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("live_mds", help="MDS 实时订阅 + 下单").add_argument(
        "-c", "--config", type=Path, required=True, help="YAML 配置文件"
    )
    # 其它子命令 …
    return p

async def _run_live_mds(cfg: dict):
    # 1）用 MarketDataProvider.from_config 构造 MDS 实时提供器
    provider = MarketDataProvider.from_config(cfg["data"], live=True)
    # 2）策略／风控／撮合模块
    strategy = BaseStrategy.from_config(cfg["strategy"])
    risk     = RiskManager(**cfg["risk"])
    broker   = LiveBroker.from_config(cfg["broker"])

    _LOG.info("🔗 开始订阅行情并驱动下单 …")
    async for snap in provider.subscribe():
        _LOG.debug("📡 快照：%s", snap)
        # 3）把 snapshot 转成策略需要的 tick/bar
        orders = strategy.on_snapshot(snap)  # 你可以扩展 BaseStrategy 支持 on_snapshot
        orders = risk.validate(orders)
        if orders:
            await broker.send_orders(orders)
            fills = await broker.fetch_fills()
            risk.update(fills)

def main():
    args = build_parser().parse_args()
    cfg = load_yaml(args.config)
    if args.command == "live_mds":
        asyncio.run(_run_live_mds(cfg))
    # … 其它分支 …

if __name__ == "__main__":
    main()
