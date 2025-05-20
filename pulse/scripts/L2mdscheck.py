# -*- coding: utf-8 -*-
"""
用已有的 MdsSpiLite 订阅并打印 L2 快照
"""
import sys, time
from pathlib import Path
from typing import Any

# ─── 定位项目根 & 把 SDK 包加入路径 ───────────
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT / "pulse" / "vendor"))

from vendor.quote_api import (
    MdsClientApi, MdsAsyncApiChannelT,
    MDSAPI_CFG_DEFAULT_SECTION, MDSAPI_CFG_DEFAULT_KEY_TCP_ADDR,
)
from pulse.api.quote.mds_spi_lite import MdsSpiLite
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
_LOG = logging.getLogger("L2Check")

def main():
    cfg_file = PROJECT_ROOT / "config" / "mds_client_sample.conf"
    symbols  = ["600000", "000001"]

    api = MdsClientApi()
    if not api.create_context(str(cfg_file)):
        _LOG.error("❌ create_context 失败")
        return

    # 用你已经写好的 MdsSpiLite
    # 通过 subscribe_config 告诉它要订阅 L2 快照（MDS_SUB_DATA_TYPE_L2_SNAPSHOT）
    spi = MdsSpiLite(
        config_file=str(cfg_file),
        subscribe_config={
            "subscriptions": [
                {
                    "codes": symbols,
                    "exchange_id": 1,        # 上交所
                    "product_type": 1,
                    "sub_mode": 0,           # SET
                    "data_types": 0x08       # MDS_SUB_DATA_TYPE_L2_SNAPSHOT (0x08)
                },
                {
                    "codes": symbols,
                    "exchange_id": 2,        # 深交所
                    "product_type": 1,
                    "sub_mode": 1,           # APPEND
                    "data_types": 0x08
                }
            ]
        }
    )

    api.register_spi(spi, add_default_channel=False)
    ch = api.add_channel_from_file(
        "l2_channel",
        str(cfg_file),
        MDSAPI_CFG_DEFAULT_SECTION,
        MDSAPI_CFG_DEFAULT_KEY_TCP_ADDR,
        # user_info 在你的 MdsSpiLite.on_connect 会被忽略，
        # subscribe_config 已经带上了所有订阅逻辑
        None, None, True
    )
    if not ch or not api.start():
        _LOG.error("❌ 通道启动失败")
        return

    _LOG.info("⏳ 等待 L2 快照，按 Ctrl+C 退出…")
    try:
        while api.is_api_running():
            time.sleep(1)
    except KeyboardInterrupt:
        pass

    api.release()
    _LOG.info("✅ 已退出")

if __name__ == "__main__":
    main()
