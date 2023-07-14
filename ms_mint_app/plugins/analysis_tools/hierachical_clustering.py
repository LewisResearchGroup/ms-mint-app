from dash import html, dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from ms_mint.notebook import Mint
from ms_mint.standards import MINT_RESULTS_COLUMNS

from ... import tools as T


_label = "Hierachical Clustering"

_options = ["Transposed"]

options = [{"value": x, "label": x} for x in _options]

metrics_options = [{"value": x, "label": x.capitalize()} for x in [
    'braycurtis', 'canberra', 'chebyshev', 'cityblock', 'correlation', 'cosine',
    'dice', 'euclidean', 'hamming', 'jaccard', 'jensenshannon', 'kulsinski',
    'mahalanobis', 'matching', 'minkowski', 'rogerstanimoto', 'russellrao',
    'seuclidean', 'sokalmichener', 'sokalsneath', 'sqeuclidean', 'yule']
]



_layout = html.Div(
    [
        html.H3(_label),
        dbc.Row([
            dbc.Col([
                dbc.Row([
                    dbc.Label('Figure width'),
                    dcc.Input(
                        id="hc-figsize-x", placeholder="Figure size x", value=8, type="number"
                    ),
                    dbc.Label('Figure height'),
                    dcc.Input(
                        id="hc-figsize-y", placeholder="Figure size x", value=8, type="number"
                    ),
                    dbc.Label('Options'), 
                    dcc.Dropdown(id="hc-options", options=options, value=[]),
                ]),

            ]),      
            
            dbc.Col([
                dbc.Row([dbc.Label('Metric X'), dcc.Dropdown(id='hc-metric-x', options=metrics_options, value='cosine')]),
                dbc.Row([dbc.Label('Metric Y'), dcc.Dropdown(id='hc-metric-y', options=metrics_options, value='cosine')]),
            ]),            
        ]),

        dbc.Button("Update", id="hc-update"),

        dcc.Loading(
            html.Div(
                id="hc-figures",
                style={
                    "margin": "auto",
                    "text-align": "center",
                    "maxWidth": "100%",
                    "minHeight": "300px",
                },
            )
        ),
    ]
)

_ouptuts = html.Div([])


def layout():
    return _layout


def callbacks(app, fsc, cache):
    @app.callback(
        Output("hc-figures", "children"),
        Input("hc-update", "n_clicks"),
        State("hc-metric-x", "value"),
        State("hc-metric-y", "value"),        
        State("hc-figsize-x", "value"),
        State("hc-figsize-y", "value"),
        State("hc-options", "value"),
        State("ana-var-name", "value"),
        State("ana-colorby", "value"),
        State("ana-groupby", "value"),
        State("ana-scaler", "value"),
        State("ana-apply", "value"),
        State("ana-file-types", "value"),
        State("ana-peak-labels-include", "value"),
        State("ana-peak-labels-exclude", "value"),
        State("wdir", "children"),
    )
    def create_figure(
        n_clicks,
        metrix_x,
        metrix_y,
        fig_size_x,
        fig_size_y,
        options,
        var_name,
        colorby,
        groupby,
        scaler,
        apply,
        file_types,
        include_labels,
        exclude_labels,
        wdir,
    ):

        if n_clicks is None:
            raise PreventUpdate

        if options is None: 
            options = []
        
        mint = Mint()

        if fig_size_x is None:
            fig_size_x = 8
        if fig_size_y is None:
            fig_size_y = 8

        fig_size_x = min(float(fig_size_x), 100)
        fig_size_y = min(float(fig_size_y), 100)

        df = T.get_complete_results(
            wdir,
            include_labels=include_labels,
            exclude_labels=exclude_labels,
            file_types=file_types,
        )
    
        mint.results = df[MINT_RESULTS_COLUMNS]
        mint.load_metadata(T.get_metadata_fn(wdir))

        fig = mint.plot.hierarchical_clustering(
            figsize=(fig_size_x, fig_size_y), 
            transposed="Transposed" in options, 
            metric=(metrix_x, metrix_y), 
            groupby=groupby, 
            scaler=scaler,
            apply=apply
        )

        src = T.fig_to_src(fig.figure)

        return html.Img(src=src, style={"maxWidth": "80%"})
