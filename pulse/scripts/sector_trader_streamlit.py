import streamlit as st
import pandas as pd
import math
import random
from datetime import datetime
from pathlib import Path

# -----------------------------
# 数据加载
# -----------------------------
SECTOR_CSV = Path("pulse/resources/sector_map.csv")  # 请放置 symbol,sector 两列

if SECTOR_CSV.exists():
    df_sector = pd.read_csv(SECTOR_CSV, dtype={"symbol": str, "sector": str})
    sectors = sorted(df_sector["sector"].unique())
else:
    st.warning("找不到 sector_map.csv，将使用演示数据！")
    demo = {
        "symbol": [
            # 银行 6 只
            "600000", "600016", "601988", "000001", "601328", "601398",
            # 券商 3 只
            "600030", "601377", "600837",
            # 地产 3 只
            "000002", "600048", "600383",
            # 家电 3 只
            "000651", "000333", "600690",
            # 新能源 4 只
            "002594", "300750", "601012", "688567"
        ],
        "name": [
            "浦发银行", "民生银行", "中国银行", "平安银行", "交通银行", "工商银行",
            "中信证券", "兴业证券", "海通证券",
            "万 科A", "保利发展", "金地集团",
            "格力电器", "美的集团", "青岛海尔",
            "比亚迪", "宁德时代", "隆基绿能", "孚能科技"
        ],
        "sector": [
            "银行", "银行", "银行", "银行", "银行", "银行",
            "券商", "券商", "券商",
            "地产", "地产", "地产",
            "家电", "家电", "家电",
            "新能源", "新能源", "新能源", "新能源"
        ],
        # 随便给一些市值(亿)示例
        "cap": [900, 800, 1500, 700, 1400, 2500, 3000, 1200, 1100, 2500, 3000, 1800, 2800, 3800, 2600, 6000, 12000, 5000, 800]
    }
    df_sector = pd.DataFrame(demo)
    sectors = sorted(df_sector["sector"].unique())

# -----------------------------
# 页面
# -----------------------------
st.set_page_config(page_title="Sector Trader", layout="wide")
st.title("板块批量买入工具")

# 自定义CSS：将确认按钮改为蓝色
st.markdown("""
<style>
div.stButton > button[kind="primary"] {
    background-color: #0066CC !important;
    border-color: #0066CC !important;
    color: white !important;
    white-space: nowrap;
}
div.stButton > button[kind="primary"]:hover {
    background-color: #004499 !important;
    border-color: #004499 !important;
    color: white !important;
}
div.stButton > button[kind="primary"]:active {
    background-color: #003366 !important;
    border-color: #003366 !important;
    color: white !important;
}
/* 普通按钮也不换行 */
div.stButton > button {
    white-space: nowrap;
}
/* 缩窄下拉框宽度(约为当前一半) */
div[data-testid="stSelectbox"], div[data-testid="stNumberInput"] {
    width: 100% !important;
    margin-right: 4px;
}
/* st.metric 数值省略号处理 */
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    overflow: visible !important;
    white-space: nowrap;
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

# 兼容不同版本 Streamlit 的重载函数
def _do_rerun():
    """在低/高版本中选择可用的 rerun 接口"""
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()

col_left, col_right = st.columns([1, 4])

with col_left:
    sector = st.selectbox("板块", sectors)
    budget_total = st.number_input("总资金(元)", value=8_000_000, step=10000)
    per_stock = st.number_input("每股预算(元)", value=40_000, step=10_000)

    st.markdown("---")

    # 为后续逻辑提供占位符，初值为False
    btn_execute = False
    btn_execute_sell = False
    btn_cancel_all = False

    # --------------------- 行情控制 ---------------------
    st.subheader("行情控制")

    col_q1, col_q2, col_q3 = st.columns([2, 2.4, 2], gap="small")
    with col_q1:
        btn_gen_quote = st.button("生成/重置行情", use_container_width=True)
    with col_q2:
        btn_update_quote = st.button("更新行情 (±10%)", use_container_width=True)
    with col_q3:
        btn_refresh_pos = st.button("刷新持仓", use_container_width=True)
    st.markdown("---")

# ----------------------------------
# 初始化买/卖各自的价格来源 session_state
# ----------------------------------
if "price_side_buy" not in st.session_state:
    st.session_state["price_side_buy"] = "SELL1 卖一价"
if "price_side_sell" not in st.session_state:
    st.session_state["price_side_sell"] = "BUY1 买一价"

# -----------------------------
# 行情工具函数 (需在初始化前定义)
# -----------------------------

# 提前定义 get_mock_quote，供后续函数调用
def get_mock_quote(symbol: str, reference_price: float | None = None) -> dict:
    """生成模拟盘口 (SELL1-5, BUY1-5, LAST)。

    如果给定 reference_price，则随机在 ±10% 以内波动；否则随机 8~15 元。
    """
    if reference_price is None:
        base = random.uniform(8, 15)
    else:
        low = reference_price * 0.9
        high = reference_price * 1.1
        base = random.uniform(low, high)

    base = round(base, 2)
    tick = 0.02
    quote = {"LAST": base}
    for i in range(1, 6):
        quote[f"SELL{i}"] = round(base + i * tick, 2)
    for i in range(1, 6):
        quote[f"BUY{i}"] = round(base - i * tick, 2)
    return quote

def _generate_quotes_df(symbols: list[str], base_map: dict[str, float] | None = None) -> pd.DataFrame:
    """为 symbols 生成五档行情 DataFrame"""
    recs = []
    for sym in symbols:
        ref = base_map.get(sym) if base_map else None
        quote = get_mock_quote(sym, ref)
        recs.append({"symbol": sym, **quote})
    return pd.DataFrame(recs)

# -----------------------------
# 行情初始化/更新 (依赖按钮)
# -----------------------------

symbols_all = df_sector["symbol"].tolist()
if "quotes_df" not in st.session_state or btn_gen_quote:
    st.session_state["quotes_df"] = _generate_quotes_df(symbols_all)
elif btn_update_quote:
    last_prices = {row.symbol: row.LAST for row in st.session_state["quotes_df"].itertuples()}
    st.session_state["quotes_df"] = _generate_quotes_df(symbols_all, base_map=last_prices)

df_quotes = st.session_state["quotes_df"]

# -----------------------------
# 持仓数据 (模拟)
# -----------------------------

def _generate_mock_positions() -> pd.DataFrame:
    """随机生成模拟持仓数据"""
    positions = []
    for _, row in df_sector.iterrows():
        qty = random.choice([0, 0, 0, 100, 200, 300, 500, 1000, 2000])
        if qty == 0:
            continue
        # choose_price 可能稍后才定义，故做兼容处理
        cost_price = choose_price(row.symbol, "BUY1") if 'choose_price' in globals() else round(random.uniform(8, 15), 2)
        positions.append({
            "symbol": row.symbol,
            "名称": row["name"],
            "sector": row.sector,
            "持仓": qty,
            "成本价": cost_price,
            "市值": qty * cost_price
        })
    return pd.DataFrame(positions)

# 初始化持仓
if "positions_df" not in st.session_state:
    st.session_state["positions_df"] = pd.DataFrame(columns=["symbol", "名称", "sector", "持仓", "成本价"])
elif btn_refresh_pos:
    # 刷新持仓只更新市值等，不重新生成
    st.session_state["positions_df"] = st.session_state["positions_df"].copy()

# 初始化资金
if "cash" not in st.session_state:
    st.session_state["cash"] = 0.0  # 0 表示尚未入金，首次买入时以预算作为初始资金
if "initial_assets" not in st.session_state:
    st.session_state["initial_assets"] = 0.0
if "trades" not in st.session_state:
    st.session_state["trades"] = []

# 选定板块过滤
df_positions = st.session_state["positions_df"]
df_positions_sector = df_positions[df_positions["sector"] == sector] if not df_positions.empty else pd.DataFrame()

# -----------------------------
# 右侧区域使用 tabs 分隔显示
# -----------------------------
# 根据按钮点击自动切换tab
if btn_execute:
    st.session_state["active_tab"] = "买入预览"
    st.session_state["trigger_tab"] = "买入预览"
elif btn_execute_sell:
    st.session_state["active_tab"] = "卖出预览"
    st.session_state["trigger_tab"] = "卖出预览"

# 如果没有设置过active_tab，默认显示买入预览
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "买入预览"

# 根据active_tab调整tab顺序，将活跃tab放在第一位
all_tabs = ["买入预览", "卖出预览", "当前持仓", "交易明细"]
active_tab = st.session_state["active_tab"]
if active_tab in all_tabs:
    tab_order = [active_tab] + [t for t in all_tabs if t != active_tab]
else:
    tab_order = all_tabs

# 创建tabs（无 key 参数，确保兼容旧版 Streamlit）
tabs_created = col_right.tabs(["买入预览", "卖出预览", "当前持仓", "交易明细"])  # 固定顺序

# 若需要切换，注入一次性 JS 点击对应标签
if "trigger_tab" in st.session_state:
    name = st.session_state["trigger_tab"]
    idx_map = {"买入预览": 0, "卖出预览": 1, "当前持仓": 2, "交易明细": 3}
    if name in idx_map:
        target_idx = idx_map[name]
        st.markdown(f"""
        <script>
        const tabButtons = parent.document.querySelectorAll('button[role="tab"]');
        if (tabButtons.length > {target_idx}) {{
            tabButtons[{target_idx}].click();
        }}
        </script>
        """, unsafe_allow_html=True)
    # 清除标志
    del st.session_state["trigger_tab"]

# 将tabs分配给对应变量
tab_mapping = {name: tabs_created[i] for i, name in enumerate(["买入预览", "卖出预览", "当前持仓", "交易明细"])}
tab_buy = tab_mapping["买入预览"]
tab_sell = tab_mapping["卖出预览"]
tab_pos = tab_mapping["当前持仓"]
tab_trades = tab_mapping["交易明细"]

with tab_pos:
    col_left_pos, col_right_pos = st.columns([1, 4])

    with col_left_pos:
        st.subheader("查看持仓")
        view_choice = st.radio("视图", ["当前板块持仓", "总持仓"], index=0, label_visibility="collapsed")

        # 资金汇总
        cash_available = st.session_state.get("cash", 0.0)
        total_market_value_tmp = 0.0
        if not df_positions.empty:
            df_tmp = df_positions.copy()
            df_tmp["最新价"] = pd.to_numeric(df_tmp["symbol"].map(df_quotes.set_index("symbol")["LAST"]), errors="coerce").fillna(0.0)
            df_tmp["持仓"] = pd.to_numeric(df_tmp["持仓"], errors="coerce").fillna(0)
            df_tmp["市值"] = (df_tmp["持仓"] * df_tmp["最新价"]).round(2)
            total_market_value_tmp = df_tmp["市值"].sum()

        total_assets = cash_available + total_market_value_tmp
        initial_assets = st.session_state.get("initial_assets", total_assets) if st.session_state.get("initial_assets", 0) > 0 else total_assets
        if st.session_state.get("initial_assets", 0) == 0:
            st.session_state["initial_assets"] = total_assets
            initial_assets = total_assets
        pnl_total = total_assets - initial_assets
        pnl_pct = (pnl_total / initial_assets * 100) if initial_assets else 0.0

        st.markdown("### 资金汇总")
        st.metric("可用资金", f"{cash_available:,.2f} 元")
        st.metric("总资产", f"{total_assets:,.2f} 元")
        st.metric("累计盈亏", f"{pnl_total:,.2f} 元", f"{pnl_pct:.2f}%")

    with col_right_pos:
        if view_choice == "当前板块持仓":
            st.subheader(f"{sector} 板块持仓")
            if df_positions_sector.empty:
                st.write("_所选板块暂无持仓_")
            else:
                df_positions_sector = df_positions_sector.copy()
                df_positions_sector["最新价"] = pd.to_numeric(df_positions_sector["symbol"].map(df_quotes.set_index("symbol")["LAST"]), errors="coerce").fillna(0.0)
                df_positions_sector["持仓"] = pd.to_numeric(df_positions_sector["持仓"], errors="coerce").fillna(0)
                df_positions_sector["市值"] = (df_positions_sector["持仓"] * df_positions_sector["最新价"]).round(2)
                df_positions_sector["浮盈"] = ((df_positions_sector["最新价"] - df_positions_sector["成本价"]) * df_positions_sector["持仓"]).round(2)
                df_positions_sector["盈亏%"] = ((df_positions_sector["浮盈"] / (df_positions_sector["成本价"] * df_positions_sector["持仓"])) * 100).round(2)

                df_pos_show = df_positions_sector[["symbol", "名称", "持仓", "成本价", "最新价", "市值", "浮盈", "盈亏%"]].rename(columns={
                    "symbol": "代码",
                    "成本价": "成本价(元)",
                    "最新价": "最新价(元)",
                    "市值": "市值(元)",
                    "浮盈": "浮盈(元)",
                    "盈亏%": "盈亏%"
                })

                st.dataframe(df_pos_show, use_container_width=True)
        else:
            st.subheader("总持仓")
            if df_positions.empty:
                st.write("_暂无任何持仓_")
            else:
                # compute df_all_show similar to previous
                df_all_positions = df_positions.copy()
                df_all_positions["最新价"] = pd.to_numeric(df_all_positions["symbol"].map(df_quotes.set_index("symbol")["LAST"]), errors="coerce").fillna(0.0)
                df_all_positions["持仓"] = pd.to_numeric(df_all_positions["持仓"], errors="coerce").fillna(0)
                df_all_positions["市值"] = (df_all_positions["持仓"] * df_all_positions["最新价"]).round(2)
                df_all_positions["浮盈"] = ((df_all_positions["最新价"] - df_all_positions["成本价"]) * df_all_positions["持仓"]).round(2)
                df_all_positions["盈亏%"] = ((df_all_positions["浮盈"] / (df_all_positions["成本价"] * df_all_positions["持仓"])) * 100).round(2)

                df_all_show = df_all_positions[["symbol", "名称", "sector", "持仓", "成本价", "最新价", "市值", "浮盈", "盈亏%"]].rename(columns={
                    "symbol": "代码",
                    "sector": "板块",
                    "成本价": "成本价(元)",
                    "最新价": "最新价(元)",
                    "市值": "市值(元)",
                    "浮盈": "浮盈(元)",
                    "盈亏%": "盈亏%"
                })
                st.dataframe(df_all_show, use_container_width=True)

# -----------------------------
# 卖出比例默认值
# -----------------------------
if "sell_ratio_label" not in st.session_state:
    st.session_state["sell_ratio_label"] = "1/5"

sell_ratio_label = st.session_state["sell_ratio_label"]

# -----------------------------
# 卖出预览逻辑（每次刷新自动计算）
# -----------------------------

if True:
    # 模拟持仓数据：这里随机生成，实际应从交易接口查询
    syms = df_sector.loc[df_sector["sector"] == sector, "symbol"].tolist()
    lot = 100
    fraction_map = {"1/5": 0.2, "1/4": 0.25, "1/3": 1/3, "1/2": 0.5, "全卖": 1.0}
    ratio = fraction_map.get(st.session_state["sell_ratio_label"], 0.2)

    records = []
    total_value = 0

    for s in syms:
        # 获取真实持仓数量
        pos_match = df_positions[df_positions["symbol"] == s]
        if pos_match.empty:
            continue
        holding_qty = int(pos_match["持仓"].iloc[0])
        cost_price_ref = float(pos_match["成本价"].iloc[0])

        quote = get_mock_quote(s, cost_price_ref)
        side_tag = st.session_state["price_side_sell"].split()[0]
        price = quote.get(side_tag, quote["LAST"])
        sell_qty = math.floor(holding_qty * ratio / lot) * lot
        if sell_qty == 0:
            continue
        value = sell_qty * price
        info = df_sector.loc[df_sector["symbol"] == s].iloc[0]
        records.append({
            "symbol": s,
            "名称": info.get("name", "-"),
            "持仓": holding_qty,
            "卖价": price,
            "卖出数量": sell_qty,
            "卖出金额": value
        })
        total_value += value

    if not records:
        with tab_sell:
            st.subheader("卖出预览")
            st.warning("无可卖持仓，或卖出数量为0！")
            
            # 处理无持仓时的卖出按钮点击
            if btn_execute_sell:
                st.error(f"当前 {sector} 板块无可卖持仓，或卖出数量为0！请先买入股票。")
    else:
        df_sell = pd.DataFrame(records)
        # 格式化
        float_cols = ["卖价", "卖出金额"]
        int_cols = ["持仓", "卖出数量"]
        for c in float_cols:
            df_sell[c] = pd.to_numeric(df_sell[c], errors="coerce").fillna(0.0)
        for c in int_cols:
            df_sell[c] = pd.to_numeric(df_sell[c], errors="coerce").fillna(0).astype(int)

        styled_sell = (
            df_sell.style
            .format({"卖价": "{:,.2f}", "卖出金额": "{:,.2f}", "持仓": "{:,}", "卖出数量": "{:,}"})
            .set_properties(subset=float_cols + int_cols, **{"font-weight": "bold", "font-size": "18px"})
            .set_table_styles([{"selector": "th", "props": [("text-align", "center")] }])
        )

        with tab_sell:
            col_left_sell, col_right_sell = st.columns([1, 4])
            with col_left_sell:
                # 价格来源 BUY1~BUY5
                opt_sell_ps = [f"BUY{i} 买{i}价" for i in range(1,6)]
                current_sell_ps = st.session_state.get("price_side_sell", opt_sell_ps[0])
                if current_sell_ps not in opt_sell_ps:
                    current_sell_ps = opt_sell_ps[0]
                    st.session_state["price_side_sell"] = current_sell_ps
                new_ps_sell = st.selectbox("价格来源", opt_sell_ps, index=opt_sell_ps.index(current_sell_ps))
                if new_ps_sell != st.session_state["price_side_sell"]:
                    st.session_state["price_side_sell"] = new_ps_sell
                    _do_rerun()

                new_ratio = st.selectbox(
                    "卖出比例",
                    ["1/5", "1/4", "1/3", "1/2", "全卖"],
                    index=["1/5", "1/4", "1/3", "1/2", "全卖"].index(st.session_state["sell_ratio_label"]),
                )
                if new_ratio != st.session_state["sell_ratio_label"]:
                    st.session_state["sell_ratio_label"] = new_ratio
                    _do_rerun()

                if "show_sell_confirm" not in st.session_state:
                    st.session_state["show_sell_confirm"] = False

                cols_sell_btn = st.columns([1,1,1])
                with cols_sell_btn[1]:
                    btn_execute_sell = st.button("一键卖出", key="btn_exec_sell", use_container_width=True)

                if btn_execute_sell:
                    st.session_state["sell_data"] = {
                        "sector": sector,
                        "total_value": total_value,
                        "sell_rows": df_sell,
                    }
                    st.session_state["show_sell_confirm"] = True

                if st.session_state.get("show_sell_confirm", False):
                    st.markdown("---")
                    st.warning("⚠️ 确认卖出？")
                    st.markdown(f"**板块：** {st.session_state['sell_data']['sector']}")
                    st.markdown(f"**总金额：** {st.session_state['sell_data']['total_value']:,.2f} 元")
                    
                    c_ok, c_cancel = st.columns(2, gap="small")
                    with c_ok:
                        if st.button("✅ 确认", key="confirm_sell_yes_tab", type="primary", use_container_width=True):
                            # 执行卖出逻辑
                            df_sell_confirm = st.session_state['sell_data']['sell_rows']
                            total_value_confirm = st.session_state['sell_data']['total_value']
                            
                            # 更新持仓与交易记录
                            for _, row in df_sell_confirm.iterrows():
                                sym = row["symbol"]
                                sell_qty = int(row["卖出数量"])
                                sell_price = float(row["卖价"])
                                # 更新持仓
                                pos_df = st.session_state["positions_df"]
                                idx_match = pos_df[pos_df["symbol"] == sym].index
                                if len(idx_match) == 0:
                                    continue  # 理论上不会发生
                                idx = idx_match[0]
                                new_qty = pos_df.at[idx, "持仓"] - sell_qty
                                if new_qty <= 0:
                                    pos_df.drop(idx, inplace=True)
                                    pos_df.reset_index(drop=True, inplace=True)
                                else:
                                    pos_df.at[idx, "持仓"] = new_qty
                                    last_p = df_quotes.set_index("symbol").at[sym, "LAST"]
                                    pos_df.at[idx, "市值"] = new_qty * last_p

                                # 记录交易
                                st.session_state["trades"].insert(0, {  # 最新的插入到最前面
                                    "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "方向": "卖出",
                                    "代码": sym,
                                    "数量": sell_qty,
                                    "价格": sell_price,
                                    "金额": sell_qty * sell_price,
                                })

                            # 更新现金
                            st.session_state["cash"] += float(total_value_confirm)
                            
                            # 设置成交提示
                            st.session_state["trade_success"] = f"✅ {sector} 板块卖出成功！总金额 {total_value_confirm:,.2f} 元"
                            
                            # 清除确认状态
                            del st.session_state["show_sell_confirm"]
                            del st.session_state["sell_data"]
                            
                            _do_rerun()
                    
                    with c_cancel:
                        if st.button("❌ 取消", key="confirm_sell_no_tab", use_container_width=True):
                            # 清除确认状态
                            del st.session_state["show_sell_confirm"]
                            del st.session_state["sell_data"]
                            _do_rerun()

                # 卖出成功提示（左栏显示）
                if "trade_success" in st.session_state and "卖出" in st.session_state["trade_success"]:
                    st.success(st.session_state["trade_success"])
                    del st.session_state["trade_success"]

            with col_right_sell:
                st.subheader("卖出预览")
                st.write(styled_sell, unsafe_allow_html=True)
                st.write(f"**预计卖出金额:** {total_value:,.2f} 元")

# -------------------------------------------------
# 交易明细 TAB
# -------------------------------------------------
with tab_trades:
    st.subheader("交易明细")
    if "trades" not in st.session_state or len(st.session_state["trades"]) == 0:
        st.write("_暂无交易记录_")
    else:
        df_trades = pd.DataFrame(st.session_state["trades"])
        float_cols_t = ["价格", "金额"]
        int_cols_t = ["数量"]
        for c in float_cols_t:
            df_trades[c] = pd.to_numeric(df_trades[c], errors="coerce").fillna(0.0)
        for c in int_cols_t:
            df_trades[c] = pd.to_numeric(df_trades[c], errors="coerce").fillna(0).astype(int)

        styled_trades = (
            df_trades.style
            .format({"价格": "{:,.2f}", "金额": "{:,.2f}", "数量": "{:,}"})
            .set_properties(subset=float_cols_t + int_cols_t, **{"font-weight": "bold", "font-size": "18px"})
        )
        st.write(styled_trades, unsafe_allow_html=True)

# -----------------------------
# 工具函数
# -----------------------------

def choose_price(symbol: str, side: str) -> float:
    """演示用: 给不同档位生成轻微不同的随机价格"""
    random.seed(hash(symbol))
    base = random.uniform(8, 15)
    if side.startswith("SELL2"):  # 卖二稍高
        base += 0.05
    elif side.startswith("SELL1"):
        base += 0.02
    elif side.startswith("BUY1"):
        base -= 0.02
    elif side.startswith("BUY2"):
        base -= 0.04
    return round(base, 2)

# -----------------------------
# 买入预览逻辑（每次刷新自动计算）
# -----------------------------

# 计算买入预览数据
syms_buy = df_sector.loc[df_sector["sector"] == sector, "symbol"].tolist()
lot = 100
records_buy = []
spent_buy = 0.0

for sym in syms_buy:
    pos_match = df_positions[df_positions["symbol"] == sym]
    ref_price = pos_match["成本价"].iloc[0] if not pos_match.empty else None
    quote_tmp = get_mock_quote(sym, ref_price)
    side_tag = st.session_state["price_side_buy"].split()[0]
    price_series = df_quotes.set_index("symbol")[side_tag]
    price_val = float(price_series.get(sym, choose_price(sym, st.session_state["price_side_buy"])))
    qty_val = math.floor(per_stock / price_val / lot) * lot
    exist_qty = int(pos_match["持仓"].iloc[0]) if not pos_match.empty else 0
    amt_val = qty_val * price_val
    info_row = df_sector[df_sector["symbol"] == sym].iloc[0]
    records_buy.append({
        "symbol": sym,
        "名称": info_row.get("name", "-"),
        "市值(亿)": info_row.get("cap", 0),
        "现有持仓": exist_qty,
        "价格": price_val,
        "数量": qty_val,
        "金额": amt_val,
    })
    spent_buy += amt_val

remain_buy = budget_total - spent_buy
df_preview_buy = pd.DataFrame(records_buy)

# 如果预算不足，按市值剔除
if remain_buy < 0:
    df_preview_buy = df_preview_buy.sort_values("市值(亿)")
    df_preview_buy["keep"] = df_preview_buy["金额"].cumsum() <= budget_total
    df_preview_buy.loc[~df_preview_buy["keep"], ["数量", "金额"]] = 0
    spent_buy = df_preview_buy["金额"].sum()
    remain_buy = budget_total - spent_buy

# ----------------- 买入 Tab 展示 -----------------

with tab_buy:
    col_left_buy, col_right_buy = st.columns([1, 4])
    with col_left_buy:
        # 价格来源选择 (卖一~卖五)
        opt_buy = [f"SELL{i} 卖{i}价" for i in range(1,6)]
        current_buy_ps = st.session_state.get("price_side_buy", opt_buy[0])
        if current_buy_ps not in opt_buy:
            current_buy_ps = opt_buy[0]
            st.session_state["price_side_buy"] = current_buy_ps
        new_ps_buy = st.selectbox("价格来源", opt_buy, index=opt_buy.index(current_buy_ps))
        if new_ps_buy != st.session_state["price_side_buy"]:
            st.session_state["price_side_buy"] = new_ps_buy
            _do_rerun()

        # 计算 buy_rows for potential confirm
        buy_rows_valid = df_preview_buy[df_preview_buy["数量"] > 0]
        total_cost_valid = buy_rows_valid["金额"].sum()

        if "show_buy_confirm" not in st.session_state:
            st.session_state["show_buy_confirm"] = False

        cols_btn = st.columns([1, 1, 1])
        with cols_btn[1]:
            btn_execute = st.button("一键买入", key="btn_exec_buy", use_container_width=True)

        if btn_execute:
            if total_cost_valid == 0:
                st.error("无有效买入数量！")
            else:
                st.session_state["buy_data"] = {"sector": sector, "total_cost": total_cost_valid, "buy_rows": buy_rows_valid}
                st.session_state["show_buy_confirm"] = True

        if st.session_state.get("show_buy_confirm", False):
            st.markdown("---")
            st.warning("⚠️ 确认买入？")
            st.markdown(f"**板块：** {st.session_state['buy_data']['sector']}")
            st.markdown(f"**总金额：** {st.session_state['buy_data']['total_cost']:,.2f} 元")

            col_ok, col_cancel = st.columns(2, gap="small")
            with col_ok:
                if st.button("✅ 确认", key="confirm_buy_yes", type="primary", use_container_width=True):
                    buy_rows = st.session_state['buy_data']['buy_rows']
                    total_cost = st.session_state['buy_data']['total_cost']

                    # ---------- 执行买入逻辑 ----------
                    for _, r in buy_rows.iterrows():
                        sym = r["symbol"]
                        qty_val = int(r["数量"])
                        price_val = float(r["价格"])
                        if qty_val == 0:
                            continue

                        pos_df = st.session_state["positions_df"]
                        idx = pos_df[pos_df["symbol"] == sym].index
                        if len(idx) == 0:
                            info = df_sector[df_sector["symbol"] == sym].iloc[0]
                            new_row = {
                                "symbol": sym,
                                "名称": info["name"],
                                "sector": info["sector"],
                                "持仓": qty_val,
                                "成本价": price_val,
                                "市值": qty_val * price_val,
                            }
                            st.session_state["positions_df"] = pd.concat([pos_df, pd.DataFrame([new_row])], ignore_index=True)
                        else:
                            idx0 = idx[0]
                            old_qty = pos_df.at[idx0, "持仓"]
                            old_cost = pos_df.at[idx0, "成本价"]
                            new_qty = old_qty + qty_val
                            new_cost = (old_cost * old_qty + price_val * qty_val) / new_qty
                            pos_df.at[idx0, "持仓"] = new_qty
                            pos_df.at[idx0, "成本价"] = round(new_cost, 3)
                            pos_df.at[idx0, "市值"] = new_qty * price_val

                    # 现金 & 交易记录
                    st.session_state["cash"] -= float(total_cost)
                    for _, r in buy_rows.iterrows():
                        st.session_state["trades"].insert(0, {
                            "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "方向": "买入",
                            "代码": r["symbol"],
                            "数量": int(r["数量"]),
                            "价格": float(r["价格"]),
                            "金额": float(r["金额"]),
                        })

                    st.session_state["trade_success"] = f"✅ {sector} 板块买入成功！总金额 {total_cost:,.2f} 元"

                    # 清理确认状态并刷新
                    del st.session_state["show_buy_confirm"]
                    del st.session_state["buy_data"]
                    _do_rerun()

            with col_cancel:
                if st.button("❌ 取消", key="confirm_buy_no", use_container_width=True):
                    del st.session_state["show_buy_confirm"]
                    del st.session_state["buy_data"]
                    _do_rerun()

        if "trade_success" in st.session_state and "买入" in st.session_state["trade_success"]:
            st.success(st.session_state["trade_success"])
            del st.session_state["trade_success"]

    # ---------- 右侧（预览表格） ----------
    with col_right_buy:
        st.subheader("预览结果")

        show_cols_b = ["symbol", "名称", "现有持仓", "价格", "数量", "金额", "市值(亿)"]
        df_show_b = df_preview_buy[show_cols_b].rename(columns={
            "symbol": "代码",
            "价格": "价格(元)",
            "数量": "股数",
            "金额": "金额(元)",
            "现有持仓": "现有持仓",
        })

        float_cols_b = ["价格(元)", "金额(元)"]
        int_cols_b = ["股数", "现有持仓", "市值(亿)"]
        for c in float_cols_b:
            df_show_b[c] = pd.to_numeric(df_show_b[c], errors="coerce").fillna(0.0)
        for c in int_cols_b:
            df_show_b[c] = pd.to_numeric(df_show_b[c], errors="coerce").fillna(0).astype(int)

        styled_b = (
            df_show_b.style
            .format({"价格(元)": "{:,.2f}", "金额(元)": "{:,.2f}", "股数": "{:,}", "现有持仓": "{:,}", "市值(亿)": "{:,}"})
            .set_properties(subset=float_cols_b + int_cols_b, **{"font-weight": "bold", "font-size": "18px"})
            .set_table_styles([{"selector": "th", "props": [("text-align", "center")] }])
        )

        st.write(styled_b, unsafe_allow_html=True)
        st.write(f"**预计投入:** {spent_buy:,.2f} 元    **余款:** {remain_buy:,.2f} 元")

        # ---------------- 执行买入 ----------------
        if btn_execute:
            buy_rows = df_preview_buy[df_preview_buy["数量"] > 0]
            total_cost = buy_rows["金额"].sum()

            if st.session_state["cash"] == 0:
                st.session_state["cash"] = float(budget_total)

            if total_cost > st.session_state["cash"]:
                st.error("现金不足，无法完成买入！")
                st.stop()

            st.session_state["show_buy_confirm"] = True
            st.session_state["buy_data"] = {"sector": sector, "total_cost": total_cost, "buy_rows": buy_rows} 