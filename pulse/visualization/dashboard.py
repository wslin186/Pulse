# pulse/visualization/dashboard.py
"""
实时监控面板 (Dash)
------------------
访问 http://127.0.0.1:8050
"""
import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
from pathlib import Path

_LOG_FILE = Path("logs").glob("*.log").__next__()

# ------ 初始数据 (启动时读最后100行日志) ------ #
def load_log_tail(n=100):
    with open(_LOG_FILE, "r", encoding="utf-8") as f:
        return list(f)[-n:]

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = dbc.Container(
    [
        html.H2("Pulse 监控面板"),
        dbc.Row(
            [
                dbc.Col(dbc.Card(
                    [dbc.CardHeader("资金曲线"),
                     dcc.Graph(id="equity")]), md=8),
                dbc.Col(dbc.Card(
                    [dbc.CardHeader("当前持仓"),
                     dash_table.DataTable(id="positions",
                                          columns=[{"name": c, "id": c} for c in ["symbol", "qty"]],
                                          data=[])])
                        , md=4),
            ],
            className="mb-4",
        ),
        dbc.Card(
            [dbc.CardHeader("最新日志(100行)"),
             dcc.Textarea(id="log", value="".join(load_log_tail()), style={"width": "100%", "height": 300})]
        ),
        dcc.Interval(id="update-interval", interval=5_000)  # 5 秒刷新
    ],
    fluid=True,
)

# ------ 回调: 每 5 秒刷新日志、资金、持仓 ------ #
@app.callback(
    Output("log", "value"),
    Input("update-interval", "n_intervals"),
)
def refresh_log(n):
    return "".join(load_log_tail())


@app.callback(
    Output("equity", "figure"),
    Input("update-interval", "n_intervals"),
)
def refresh_equity(n):
    path = Path("logs/equity_curve.parquet")
    if path.exists():
        s = pd.read_parquet(path)["equity"]
        return {"data": [{"x": s.index, "y": s.values, "mode": "lines"}]}
    return {"data": []}


@app.callback(
    Output("positions", "data"),
    Input("update-interval", "n_intervals"),
)
def refresh_pos(n):
    pfile = Path("logs/positions.parquet")
    if pfile.exists():
        df = pd.read_parquet(pfile)
        return df.to_dict("records")
    return []

def launch_dashboard():
    # Dash 3.x 用 app.run；旧版 Dash 仍兼容 run_server
    app.run(debug=False, host="0.0.0.0", port=8050)

