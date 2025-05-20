# -*- coding: utf-8 -*-
"""
Pulse 主程序入口
================

支持四大模式：
1. backtest  —— 本地历史回测
2. live      —— 实盘订阅 + 下单
3. train     —— 强化学习训练
4. dash      —— 实时监控面板

用法:
    python -m pulse <subcmd> [--config xxx.yaml] [其他参数]
"""
from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
from typing import Any

from pulse.core.utils.logger import get_logger
from pulse.core.utils.config import load_yaml
from pulse.core.data.market_data_provider import MarketDataProvider
from pulse.core.strategy.base_strategy import BaseStrategy
from pulse.core.risk.risk_manager import RiskManager
from pulse.core.execution.broker import SimBroker
from pulse.visualization.dashboard import launch_dashboard

_LOG = get_logger("Main")


# ---------- 具体模式实现 ---------- #
def run_backtest(cfg_path: Path) -> None:
    cfg = load_yaml(cfg_path)
    _LOG.info("加载回测配置: %s", cfg_path)

    data_provider = MarketDataProvider.from_config(cfg["data"])
    strategy      = BaseStrategy.from_config(cfg["strategy"])
    broker        = SimBroker(initial_cash=cfg["broker"]["initial_cash"])
    risk          = RiskManager(**cfg["risk"])

    symbol = cfg["symbols"][0]
    report = SimBroker.backtest(strategy, broker, risk, data_provider, symbol,
                                cfg["period"]["start"], cfg["period"]["end"])
    report.to_html("backtest_report.html")
    _LOG.info("✅ 回测完成，已生成 backtest_report.html")


async def _live_loop(cfg: dict[str, Any]) -> None:
    """异步行情订阅 + 下单 + 回报处理"""
    # 1. 初始化
    data_provider = MarketDataProvider.from_config(cfg["data"], live=True)
    strategy      = BaseStrategy.from_config(cfg["strategy"])
    broker        = LiveBroker.from_config(cfg["broker"])
    risk          = RiskManager(**cfg["risk"])

    # 2. 订阅行情
    _LOG.info("🔗 连接行情，订阅标的：%s", cfg["symbols"])
    async for tick in data_provider.subscribe(cfg["symbols"], fields=cfg.get("fields")):
        # 3. 策略处理
        strategy.on_tick(tick)
        # 4. 拿到策略产生的订单
        orders = strategy.pop_orders()
        # 5. 风控校验
        valid = risk.validate(orders)
        if valid:
            _LOG.info("📤 发送订单: %s", valid)
            await broker.send_orders(valid)
        # 6. 获取成交回报并更新风控
        fills = await broker.fetch_fills()
        if fills:
            _LOG.info("📈 收到回报: %s", fills)
            risk.update(fills)


def run_live(cfg_path: Path) -> None:
    from pulse.core.execution.broker import LiveBroker

    cfg = load_yaml(cfg_path)
    _LOG.info("加载实盘配置: %s", cfg_path)

    # 用 asyncio 运行整个订阅+交易协程
    asyncio.run(_live_loop(cfg))


def run_train(cfg_path: Path) -> None:
    cfg = load_yaml(cfg_path)
    _LOG.info("加载 RL 训练配置: %s", cfg_path)

    from pulse.core.strategy.rl.trainer import RLTrainer
    trainer = RLTrainer.from_config(cfg)
    trainer.train()
    trainer.save(cfg["output"])
    _LOG.info("✅ 训练完成，模型已保存到 %s", cfg["output"])


def run_dash() -> None:
    _LOG.info("启动 Dash 面板 ...")
    launch_dashboard()


# ---------- CLI 解析 ---------- #
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser("Pulse Quant Framework")
    sub = p.add_subparsers(dest="command", required=True)

    def _add_config_arg(sp):
        sp.add_argument("-c", "--config", type=Path, required=True,
                        help="YAML 配置文件路径")

    _add_config_arg(sub.add_parser("backtest", help="历史回测"))
    _add_config_arg(sub.add_parser("live",     help="实时交易"))
    _add_config_arg(sub.add_parser("train",    help="强化学习训练"))
    sub.add_parser("dash", help="启动可视化面板")

    return p


def main() -> None:
    args = build_parser().parse_args()

    if args.command == "backtest":
        run_backtest(args.config)
    elif args.command == "live":
        run_live(args.config)
    elif args.command == "train":
        run_train(args.config)
    elif args.command == "dash":
        run_dash()
    else:
        raise RuntimeError(f"Unknown command {args.command!r}")


if __name__ == "__main__":
    main()
