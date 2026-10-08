"""App shell: navigation, global filters, KPI strip, and the live-refresh clock.

Each page under pages/ owns its own charts and callbacks; they all read the
shared 'interval-component' and 'filter-store' defined here.
"""
from datetime import datetime

import dash
from dash import ALL, Input, Output, State, dcc, html

from data import (
    BORDER, BUY_COLOR, FONT_FAMILY, GOOD, INK_MUTED, INK_PRIMARY,
    INK_SECONDARY, PAGE_PLANE, REFRESH_INTERVAL_MS, STOCK_LIST, SURFACE,
    SELL_COLOR, build_kpis, fetch_all, filter_all,
)

app = dash.Dash(__name__, use_pages=True, suppress_callback_exceptions=True)
app.title = 'MarketPulse Stream'
server = app.server

KPI_DEFS = [
    ('kpi-total', 'Total Trades'),
    ('kpi-buy', 'Buy Trades'),
    ('kpi-sell', 'Sell Trades'),
    ('kpi-avgprice', 'Avg Trade Price'),
]


def build_navbar():
    links = []
    for page in dash.page_registry.values():
        links.append(dcc.Link(
            page['name'],
            href=page['relative_path'],
            id={'type': 'nav-link', 'page': page['name']},
            className='nav-link',
        ))
    return html.Nav(className='nav-bar', children=links)


app.layout = html.Div(className='app-shell', children=[
    dcc.Location(id='url'),
    dcc.Interval(id='interval-component', interval=REFRESH_INTERVAL_MS, n_intervals=0),
    dcc.Store(id='filter-store', storage_type='session'),

    html.Header(className='app-header', children=[
        html.Div(className='app-title', children=[
            html.Span('MarketPulse', className='title-accent'),
            html.Span(' Stream'),
        ]),
        html.Div(className='live-indicator', children=[
            html.Button('Pause', id='pause-button', n_clicks=0, className='pause-btn'),
            html.Span(className='live-dot', id='live-dot'),
            html.Span('LIVE', id='live-label'),
            html.Span(' · updated ', className='muted'),
            html.Span(id='kpi-updated', className='muted'),
        ]),
    ]),

    html.Div(className='filter-bar', children=[
        dcc.Dropdown(
            id='stock-filter',
            options=[{'label': s, 'value': s} for s in STOCK_LIST],
            value=STOCK_LIST,
            multi=True,
            placeholder='Filter by stock…',
            className='stock-dropdown',
        ),
        dcc.RadioItems(
            id='type-filter',
            options=[
                {'label': 'All', 'value': 'all'},
                {'label': 'Buy', 'value': 'buy'},
                {'label': 'Sell', 'value': 'sell'},
            ],
            value='all',
            inline=True,
            className='type-radio',
        ),
    ]),

    build_navbar(),

    html.Div(className='kpi-row', children=[
        html.Div(className='kpi-card', children=[
            html.Div(label, className='kpi-label'),
            html.Div('—', id=kid, className='kpi-value'),
        ]) for kid, label in KPI_DEFS
    ]),

    html.Div(dash.page_container, className='page-body'),
])


@app.callback(
    Output('filter-store', 'data'),
    Input('stock-filter', 'value'),
    Input('type-filter', 'value'),
)
def update_filter_store(stocks, trade_type):
    return {'stocks': stocks or [], 'trade_type': trade_type or 'all'}


@app.callback(
    Output('interval-component', 'disabled'),
    Output('pause-button', 'children'),
    Output('live-label', 'children'),
    Input('pause-button', 'n_clicks'),
    State('interval-component', 'disabled'),
    prevent_initial_call=True,
)
def toggle_live(_n_clicks, is_disabled):
    now_paused = not is_disabled
    return now_paused, ('Resume' if now_paused else 'Pause'), ('PAUSED' if now_paused else 'LIVE')


@app.callback(
    Output('kpi-total', 'children'),
    Output('kpi-buy', 'children'),
    Output('kpi-sell', 'children'),
    Output('kpi-avgprice', 'children'),
    Output('kpi-updated', 'children'),
    Input('interval-component', 'n_intervals'),
    Input('filter-store', 'data'),
)
def refresh_kpis(_n, filters):
    filters = filters or {}
    data = fetch_all()
    filtered = filter_all(data, filters.get('stocks'), filters.get('trade_type', 'all'))
    total, buy, sell, avg_price = build_kpis(filtered['stocks'])
    return total, buy, sell, avg_price, datetime.now().strftime('%H:%M:%S')


@app.callback(
    Output({'type': 'nav-link', 'page': ALL}, 'className'),
    Input('url', 'pathname'),
    State({'type': 'nav-link', 'page': ALL}, 'href'),
)
def highlight_active_nav(pathname, hrefs):
    return ['nav-link active' if href == pathname else 'nav-link' for href in hrefs]


app.index_string = f'''
<!DOCTYPE html>
<html>
<head>
{{%metas%}}
<title>{{%title%}}</title>
{{%favicon%}}
{{%css%}}
<style>
  :root {{ color-scheme: dark; }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: {PAGE_PLANE};
    color: {INK_PRIMARY};
    font-family: {FONT_FAMILY};
  }}
  .app-shell {{ padding: 20px 28px 40px; max-width: 1600px; margin: 0 auto; }}
  .app-header {{
    display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between;
    gap: 12px; margin-bottom: 16px;
  }}
  .app-title {{ font-size: 24px; font-weight: 600; }}
  .title-accent {{ color: {BUY_COLOR}; }}
  .live-indicator {{
    display: flex; align-items: center; gap: 8px; font-size: 13px; color: {INK_SECONDARY};
  }}
  .muted {{ color: {INK_MUTED}; }}
  .live-dot {{
    width: 8px; height: 8px; border-radius: 50%; background: {GOOD};
    box-shadow: 0 0 0 0 rgba(12,163,12,0.6);
    animation: pulse 1.6s infinite;
  }}
  @keyframes pulse {{
    0% {{ box-shadow: 0 0 0 0 rgba(12,163,12,0.6); }}
    70% {{ box-shadow: 0 0 0 6px rgba(12,163,12,0); }}
    100% {{ box-shadow: 0 0 0 0 rgba(12,163,12,0); }}
  }}
  .pause-btn {{
    background: {SURFACE}; border: 1px solid {BORDER}; color: {INK_PRIMARY};
    border-radius: 6px; padding: 5px 12px; font-size: 12px; cursor: pointer;
    font-family: {FONT_FAMILY};
  }}
  .pause-btn:hover {{ border-color: {BUY_COLOR}; }}

  .filter-bar {{
    display: flex; flex-wrap: wrap; align-items: center; gap: 16px;
    background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 10px;
    padding: 12px 16px; margin-bottom: 16px;
  }}
  .stock-dropdown {{ flex: 1; min-width: 260px; }}
  .stock-dropdown div[class*="-control"] {{
    background: {PAGE_PLANE} !important; border-color: {BORDER} !important;
  }}
  .stock-dropdown div[class*="-menu"] {{ background: {SURFACE} !important; z-index: 20; }}
  .stock-dropdown div[class*="-singleValue"],
  .stock-dropdown div[class*="-placeholder"],
  .stock-dropdown div[class*="-option"] {{ color: {INK_PRIMARY} !important; }}
  .stock-dropdown div[class*="-multiValue"] {{
    background: #24241f !important; border: 1px solid {BORDER} !important;
  }}
  .stock-dropdown div[class*="-multiValue"] div {{ color: {INK_PRIMARY} !important; }}
  .stock-dropdown input {{ color: {INK_PRIMARY} !important; }}
  .type-radio label {{
    margin-right: 14px; color: {INK_SECONDARY}; font-size: 13px; cursor: pointer;
  }}
  .type-radio input {{ margin-right: 4px; accent-color: {BUY_COLOR}; cursor: pointer; }}

  .nav-bar {{ display: flex; gap: 8px; margin-bottom: 20px; flex-wrap: wrap; }}
  .nav-link {{
    color: {INK_SECONDARY}; text-decoration: none; font-size: 13px; font-weight: 600;
    padding: 8px 16px; border-radius: 999px; border: 1px solid {BORDER};
    background: {SURFACE};
  }}
  .nav-link:hover {{ color: {INK_PRIMARY}; border-color: {BUY_COLOR}; }}
  .nav-link.active {{ color: {PAGE_PLANE}; background: {BUY_COLOR}; border-color: {BUY_COLOR}; }}

  .kpi-row {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px; margin-bottom: 24px;
  }}
  .kpi-card {{
    background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 10px;
    padding: 16px 20px;
  }}
  .kpi-label {{
    color: {INK_MUTED}; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em;
  }}
  .kpi-value {{ color: {INK_PRIMARY}; font-size: 26px; font-weight: 600; margin-top: 6px; }}

  .chart-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
    gap: 20px; margin-bottom: 24px;
  }}
  .chart-card {{
    background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 10px;
    padding: 8px; overflow: hidden;
  }}
  .table-card {{
    background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 10px;
    padding: 16px 20px; margin-bottom: 24px;
  }}
  .table-title {{ margin: 0 0 12px; font-size: 15px; font-weight: 600; color: {INK_PRIMARY}; }}
</style>
</head>
<body>
{{%app_entry%}}
<footer>
{{%config%}}
{{%scripts%}}
{{%renderer%}}
</footer>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8050)
