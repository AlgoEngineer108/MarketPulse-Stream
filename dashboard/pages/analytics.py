import dash
from dash import Input, Output, dcc, html

from data import (
    AREA_COLORS, SEQUENTIAL_BLUES, TRADE_COLORS, create_figure, fetch_all,
    filter_all,
)

dash.register_page(__name__, path='/analytics', name='Analytics', order=2)

CHARTS = [
    'histogram-chart',
    'heatmap-chart',
    'area-chart',
    'time-series-chart',
    'treemap-chart',
    'sunburst-chart',
    'violin-chart',
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
def refresh_analytics(_n, filters):
    filters = filters or {}
    data = fetch_all()
    f = filter_all(data, filters.get('stocks'), filters.get('trade_type', 'all'))

    figures = {
        'histogram-chart': create_figure(
            f['stocks'], 'bar', x='quantity', title='Stock Quantity Distribution'),
        'heatmap-chart': create_figure(
            f['stocks'], 'heatmap', x='price', y='quantity',
            color_continuous_scale=SEQUENTIAL_BLUES, title='Price and Quantity Density'),
        'area-chart': create_figure(
            f['pivoted'], 'area', x='stock', y=['avg_price_buy', 'avg_price_sell'],
            color_discrete_map=AREA_COLORS, title='Average Buy vs Sell Price'),
        'time-series-chart': create_figure(
            f['pivoted'], 'line', x='stock', y=['avg_price_buy', 'avg_price_sell'],
            color_discrete_map=AREA_COLORS, title='Buy vs Sell Price by Stock'),
        'treemap-chart': create_figure(
            f['analytics'], 'treemap', path=['trade_type', 'stock'], values='quantity',
            color='trade_type', color_discrete_map=TRADE_COLORS,
            title='Treemap of Stock Distribution'),
        'sunburst-chart': create_figure(
            f['analytics'], 'sunburst', path=['trade_type', 'stock'],
            values='avg_price_overall', color='trade_type',
            color_discrete_map=TRADE_COLORS, title='Sunburst of Stock Categories'),
        'violin-chart': create_figure(
            f['ranked'], 'violin', x='trade_type', y='price', color='trade_type',
            color_discrete_map=TRADE_COLORS, box=True,
            title='Violin Plot of Price Distribution'),
    }
    return [figures[gid] for gid in CHARTS]
