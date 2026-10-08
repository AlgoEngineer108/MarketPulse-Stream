import dash
from dash import Input, Output, dash_table, dcc, html

from data import (
    BUY_COLOR, FONT_FAMILY, GRIDLINE, INK_MUTED, INK_PRIMARY, SELL_COLOR,
    SURFACE, TRADE_COLORS, build_recent_trades, create_figure, fetch_all,
    filter_all,
)

dash.register_page(__name__, path='/live', name='Live Feed', order=1)

TABLE_COLUMNS = [
    {'name': 'Stock', 'id': 'stock'},
    {'name': 'Type', 'id': 'trade_type'},
    {'name': 'Price', 'id': 'price'},
    {'name': 'Qty', 'id': 'quantity'},
    {'name': 'Date', 'id': 'trade_date'},
    {'name': 'Time', 'id': 'trade_time'},
]

layout = html.Div(children=[
    html.Div(className='table-card', children=[
        html.H3('Live Trade Feed', className='table-title'),
        dash_table.DataTable(
            id='trades-table',
            columns=TABLE_COLUMNS,
            data=[],
            page_size=10,
            style_header={
                'backgroundColor': SURFACE, 'color': INK_MUTED,
                'border': f'1px solid {GRIDLINE}', 'textTransform': 'uppercase',
                'fontSize': '11px', 'letterSpacing': '0.05em',
            },
            style_cell={
                'backgroundColor': SURFACE, 'color': INK_PRIMARY,
                'border': f'1px solid {GRIDLINE}', 'fontFamily': FONT_FAMILY,
                'fontSize': '13px', 'padding': '8px 12px',
            },
            style_data_conditional=[
                {'if': {'filter_query': '{trade_type} = "buy"', 'column_id': 'trade_type'},
                 'color': BUY_COLOR, 'fontWeight': '600'},
                {'if': {'filter_query': '{trade_type} = "sell"', 'column_id': 'trade_type'},
                 'color': SELL_COLOR, 'fontWeight': '600'},
            ],
        ),
    ]),

    html.Div(className='chart-grid', children=[
        html.Div(className='chart-card', children=[
            dcc.Graph(id='scatter-plot', config={'displayModeBar': False}),
        ]),
        html.Div(className='chart-card', children=[
            dcc.Graph(id='box-plot-chart', config={'displayModeBar': False}),
        ]),
    ]),
])


@dash.callback(
    Output('trades-table', 'data'),
    Output('scatter-plot', 'figure'),
    Output('box-plot-chart', 'figure'),
    Input('interval-component', 'n_intervals'),
    Input('filter-store', 'data'),
)
def refresh_live_feed(_n, filters):
    filters = filters or {}
    data = fetch_all()
    f = filter_all(data, filters.get('stocks'), filters.get('trade_type', 'all'))

    table_data = build_recent_trades(f['stocks'])
    scatter_fig = create_figure(
        f['ranked'], 'scatter', x='quantity', y='price', color='trade_type',
        color_discrete_map=TRADE_COLORS, title='Price vs Quantity')
    box_fig = create_figure(
        f['stocks'], 'box', x='trade_type', y='price', color='trade_type',
        color_discrete_map=TRADE_COLORS, title='Price Analysis by Trade Type')

    return table_data, scatter_fig, box_fig
