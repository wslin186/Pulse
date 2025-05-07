"""
test_oes.py  —— 连接 OES 并验证 OesSpiLite
------------------------------------------
1. 连接委托 / 回报通道
2. 查询资金、持仓
3. 用演示账号发一笔查询 / 模拟委托（真正下单请改参数）
"""
import time

# ① 按你的项目路径调整
from vendor.trade_api import OesClientApi, OesOrdReqT, eOesMarketIdT, eOesBuySellTypeT, eOesOrdTypeT
from api.trade.oes_spi_lite import OesSpiLite          # ← 刚才那份 SPI

CFG_FILE = "../config/oes_client_stk.conf"                    # ← 你的 conf 路径
USER     = "demo001"                                       # ← 如需动态改用户名/密码
PWD      = "123456"

# -------------------------------------------------------------------
# 1.  创建 API + SPI
# -------------------------------------------------------------------
api  = OesClientApi(CFG_FILE)
spi  = OesSpiLite()                                        # 需要回调就传 on_any=lambda b: ...

# 如需覆盖 conf 里的账号，可以在注册 SPI 前动态设置
# api.set_user_password(USER.encode(), PWD.encode())

# 把 SPI 注册进去，同时让 API 自动按 conf 建好一个委托通道 + 回报通道
if not api.register_spi(spi, add_default_channel=True):
    raise SystemExit("❌ SPI 注册失败")

# -------------------------------------------------------------------
# 2.  启动
# -------------------------------------------------------------------
if not api.start():                                        # 非阻塞，内部起线程
    raise SystemExit("❌ 启动失败，请查日志")

# 等待通道全部连好
while not api.is_channel_connected(api.get_default_ord_channel()):
    print("⏳ 等待委托通道连接…")
    time.sleep(1)

while not api.is_channel_connected(api.get_default_rpt_channel()):
    print("⏳ 等待回报通道连接…")
    time.sleep(1)

print("✅ 通道全部就绪")

# -------------------------------------------------------------------
# 3.  查询资金 / 持仓（触发 SPI on_cash_asset_variation 等回调）
# -------------------------------------------------------------------
api.query_cash_asset()             # 资金
api.query_stk_holding()            # 持仓
time.sleep(0.2)                    # 等回调打印完

# -------------------------------------------------------------------
# 4.  演示发送一笔“A 股限价买入 600000” （**注意修改**）
# -------------------------------------------------------------------
ORDER_QTY   = 100                  # 股
ORDER_PRICE = 126700              # 报 12.67 → 4 位精度报 126700
cl_seq_no   = api.get_next_cl_seq_no()

req = OesOrdReqT(
    clSeqNo   = cl_seq_no,
    mktId     = eOesMarketIdT.OES_MKT_SH_ASHARE,
    securityId= b"600000",
    bsType    = eOesBuySellTypeT.OES_BS_TYPE_BUY,
    ordType   = eOesOrdTypeT.OES_ORD_TYPE_LMT,
    ordPrice  = ORDER_PRICE,
    ordQty    = ORDER_QTY
)

ret = api.send_order(req=req)
if ret < 0:
    print("❌ send_order 失败，检查参数或权限")
else:
    print(f"📨 已发委托 clSeqNo={cl_seq_no}")

# -------------------------------------------------------------------
# 5.  让脚本挂着观察回报，按 Ctrl‑C 退出
# -------------------------------------------------------------------
try:
    while True:
        time.sleep(5)
except KeyboardInterrupt:
    print("🛑 收到 Ctrl‑C，退出…")
finally:
    api.release()
