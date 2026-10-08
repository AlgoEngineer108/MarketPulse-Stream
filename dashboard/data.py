"""Shared Cassandra access, filtering, and figure-building helpers.

Used by dashboard.py (the app shell) and every module under pages/.
"""
import time

import pandas as pd
import plotly.express as px
from cassandra.cluster import Cluster

# ---------------------------------------------------------------------------
# Palette (dark "trading terminal" theme)
# ---------------------------------------------------------------------------
PAGE_PLANE = '#0d0d0d'
SURFACE = '#1a1a19'
INK_PRIMARY = '#ffffff'
INK_SECONDARY = '#c3c2b7'
INK_MUTED = '#898781'
GRIDLINE = '#2c2c2a'
BASELINE = '#383835'
BORDER = 'rgba(255,255,255,0.10)'
GOOD = '#0ca30c'
CRITICAL = '#e34948'

BUY_COLOR = '#3987e5'
SELL_COLOR = '#d95926'
TRADE_COLORS = {'buy': BUY_COLOR, 'sell': SELL_COLOR}
AREA_COLORS = {'avg_price_buy': BUY_COLOR, 'avg_price_sell': SELL_COLOR}
SEQUENTIAL_BLUES = ['#1a1a19', '#184f95', '#2a78d6', '#5598e7', '#9ec5f4', '#cde2fb']

FONT_FAMILY = 'system-ui, -apple-system, "Segoe UI", sans-serif'

REFRESH_INTERVAL_MS = 5000
ROW_LIMIT = 1000

# Same tickers the producer simulates trades for (kafka-producer/producer.py)
STOCK_LIST = ["AAPL", "MSFT", "GOOGL", "AMZN", "FB", "TSLA", "BRK.A", "V", "JPM",
              "JNJ", "UNH", "WMT", "PG", "MA", "DIS", "NVDA", "HD", "PYPL", "BAC", "CMCSA"]

NUMERIC_COLUMNS = ['price', 'avg_price', 'avg_price_buy',
                   'avg_price_sell', 'avg_price_overall']


# ---------------------------------------------------------------------------
# Cassandra access
# ---------------------------------------------------------------------------
def connect_with_retry(host='172.28.1.3', port=9042, retries=30, delay=2):
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            cluster = Cluster([host], port=port)
            session = cluster.connect('stockdata')
            print(f'Connected to Cassandra on attempt {attempt}')
            return session
        except Exception as exc:
            last_exc = exc
            print(f'Cassandra not ready yet (attempt {attempt}/{retries}): {exc}')
            time.sleep(delay)
    raise RuntimeError(f'Could not connect to Cassandra after {retries} attempts') from last_exc


SESSION = connect_with_retry()


def fetch_table(table_name, limit=ROW_LIMIT):
    query = f'SELECT * FROM {table_name} LIMIT {limit}'
    try:
        rows = SESSION.execute(query)
        df = pd.DataFrame(list(rows))
    except Exception as exc:
        print(f'Error querying {table_name}: {exc}')
        return pd.DataFrame()

    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = df[col].astype(float)
    for col in ('trade_date', 'trade_time'):
        if col in df.columns:
            df[col] = df[col].astype(str)
    return df


def fetch_all():
    return {
        'stocks': fetch_table('stocks'),
        'grouped': fetch_table('grouped_stocks'),
        'pivoted': fetch_table('pivoted_stocks'),
        'ranked': fetch_table('ranked_stocks'),
        'analytics': fetch_table('analytics_stocks'),
        'rollup': fetch_table('rollup_stocks'),
    }


# ---------------------------------------------------------------------------
# Filtering (applied client-side after fetch; a column only gets filtered on
# the tables that actually carry it, e.g. pivoted tables have no trade_type)
# ---------------------------------------------------------------------------
def apply_filters(df, stocks=None, trade_type='all'):
    if df.empty:
        return df
    filtered = df
    if stocks and 'stock' in filtered.columns:
        filtered = filtered[filtered['stock'].isin(stocks)]
    if trade_type and trade_type != 'all' and 'trade_type' in filtered.columns:
        filtered = filtered[filtered['trade_type'] == trade_type]
    return filtered


def filter_all(data, stocks=None, trade_type='all'):
    return {name: apply_filters(df, stocks, trade_type) for name, df in data.items()}


# ---------------------------------------------------------------------------
# Figure styling + construction
# ---------------------------------------------------------------------------
def style_fig(fig):
    if isinstance(fig, dict):
        return fig
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        font=dict(family=FONT_FAMILY, color=INK_PRIMARY, size=12),
        title_font=dict(size=15, color=INK_PRIMARY),
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color=INK_SECONDARY)),
        margin=dict(l=40, r=20, t=50, b=40),
        hoverlabel=dict(bgcolor='#24241f', font_color=INK_PRIMARY),
    )
    fig.update_xaxes(gridcolor=GRIDLINE, zerolinecolor=BASELINE, color=INK_MUTED)
    fig.update_yaxes(gridcolor=GRIDLINE, zerolinecolor=BASELINE, color=INK_MUTED)
    return fig


def create_figure(df, chart_type, **kwargs):
    if df.empty:
        print(f"No data available for {kwargs.get('title')}")
        return {}

    fig = None
    if chart_type == 'bar':
        fig = px.bar(df, **kwargs)
    elif chart_type == 'line':
        fig = px.line(df, **kwargs)
    elif chart_type == 'scatter':
        fig = px.scatter(df, **kwargs)
    elif chart_type == 'area':
        fig = px.area(df, **kwargs)
    elif chart_type == 'pie':
        fig = px.pie(df, **kwargs)
    elif chart_type == 'box':
        fig = px.box(df, **kwargs)
    elif chart_type == 'heatmap':
        fig = px.density_heatmap(df, **kwargs)
    elif chart_type == 'treemap':
        fig = px.treemap(df, **kwargs)
    elif chart_type == 'sunburst':
        fig = px.sunburst(df, **kwargs)
    elif chart_type == 'violin':
        fig = px.violin(df, **kwargs)

    if fig is None:
        return {}
    return style_fig(fig)


def build_kpis(stocks_df):
    if stocks_df.empty:
        return '0', '0', '0', '$0.00'
    total = len(stocks_df)
    buy = int((stocks_df['trade_type'] == 'buy').sum())
    sell = int((stocks_df['trade_type'] == 'sell').sum())
    avg_price = stocks_df['price'].mean()
    return f'{total:,}', f'{buy:,}', f'{sell:,}', f'${avg_price:,.2f}'


def build_recent_trades(stocks_df, limit=15):
    if stocks_df.empty:
        return []
    recent = stocks_df.copy()
    recent['ts'] = pd.to_datetime(
        recent['trade_date'].astype(str) + ' ' + recent['trade_time'].astype(str),
        errors='coerce')
    recent = recent.sort_values('ts', ascending=False).head(limit)
    recent = recent[['stock', 'trade_type', 'price', 'quantity',
                      'trade_date', 'trade_time']]
    recent['price'] = recent['price'].map(lambda p: f'{p:,.2f}')
    return recent.to_dict('records')
