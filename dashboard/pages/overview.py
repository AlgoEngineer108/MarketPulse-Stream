import dash
from dash import Input, Output, dcc, html

from data import TRADE_COLORS, create_figure, fetch_all, filter_all

dash.register_page(__name__, path='/', name='Overview', order=0)

CHARTS = [
    'bar-chart',
    'line-chart',
    'pie-chart',
    'rollup-chart',
]

layout = html.Div(className='chart-grid', children=[
    html.Div(className='chart-card', children=[
        dcc.Graph(id=gid, config={'displayModeBar': False}),
    ]) for gid in CHARTS
])


@dash.callback(
    [Output(gid, 'figure') for gid in CHARTS],
    Input('interval-component', 'n_intervals'),
    Input('filter-store', 'data'),
)
def refresh_overview(_n, filters):
    filters = filters or {}
    data = fetch_all()
    f = filter_all(data, filters.get('stocks'), filters.get('trade_type', 'all'))

    figures = {
        'bar-chart': create_figure(
            f['stocks'], 'bar', x='trade_date', y='price', color='trade_type',
            color_discrete_map=TRADE_COLORS, title='Price by Trade Date and Type'),
        'line-chart': create_figure(
            f['grouped'], 'line', x='trade_type', y='avg_price', markers=True,
            title='Average Price by Trade Type'),
        'pie-chart': create_figure(
            f['analytics'], 'pie', names='trade_type', values='avg_price_overall',
            color='trade_type', color_discrete_map=TRADE_COLORS,
            title='Overall Average Price Distribution by Trade Type'),
        'rollup-chart': create_figure(
            f['rollup'], 'bar', x='trade_date', y='avg_price', color='trade_type',
            barmode='group', color_discrete_map=TRADE_COLORS,
            title='Daily Average Price by Trade Type'),
    }
    return [figures[gid] for gid in CHARTS]
