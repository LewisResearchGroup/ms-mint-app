import numpy as np

from dash import html, dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from ms_mint.Mint import Mint
from ms_mint.plotly_tools import plotly_heatmap
from ms_mint.standards import MINT_RESULTS_COLUMNS

from ... import tools as T

_label = "Heatmap"


heatmap_options = [
    {"label": "Cluster", "value": "clustered"},
    {"label": "Dendrogram", "value": "add_dendrogram"},
    {"label": "Transposed", "value": "transposed"},
    {"label": "Correlation", "value": "correlation"},
    {"label": "Show in new tab", "value": "call_show"},
]


_layout = html.Div(
    [
        html.H3("Heatmap"),
        dbc.Button("Update", id="heatmap-update"),
        dcc.Dropdown(
            id="heatmap-options",
            value=[],
            options=heatmap_options,
            multi=True,
        ),
        dcc.Loading(
            html.Div(
                [dcc.Graph(id="heatmap-figure")],
                style={"height": "100vh", "marginTop": "50px"},
            ),
        ),
    ]
)


def layout():
    return _layout


def callbacks(app, fsc, cache):
    @app.callback(
        Output("heatmap-controls", "children"),
        Input("ana-secondary-tab", "value"),
        State("wdir", "children"),
    )
    def heat_controls(tab, wdir):
        if tab != _label:
            raise PreventUpdate
        return _layout

    @app.callback(
        Output("heatmap-figure", "figure"),
        Input("heatmap-update", "n_clicks"),
        State("ana-var-name", "value"),
        State("ana-groupby", "value"),
        State("ana-scaler", "value"),
        State("ana-apply", "value"),
        State("ana-file-types", "value"),
        State("ana-peak-labels-include", "value"),
        State("ana-peak-labels-exclude", "value"),
        State("ana-ms-order", "value"),
        State("heatmap-options", "value"),
        State("viewport-container", "children"),
        State("wdir", "children"),
    )
    def heat_heatmap(
        n_clicks,
        var_name,
        groupby,
        scaler,
        apply,
        file_types,
        include_labels,
        exclude_labels,
        ms_order,
        options,
        viewport,
        wdir,
    ):
        mint = Mint()

        width, height = [int(e) for e in viewport.split(",")]

        df = T.get_complete_results(
            wdir,
            include_labels=include_labels,
            exclude_labels=exclude_labels,
            file_types=file_types,
        )

        if len(df) == 0:
            return "No results yet. First run MINT."

        mint.results = df[MINT_RESULTS_COLUMNS]
        mint.load_metadata(T.get_metadata_fn(wdir))
        
        df = mint.crosstab(var_name=var_name, apply=apply, groupby=groupby, scaler=scaler)

        if ms_order:
            # ms_order might contain 'ms_file_label' which is the index of the dataframe
            ndx = mint.meta.reset_index().sort_values(ms_order).set_index('ms_file_label').index.to_list()
            df = df.reindex(ndx)

        desc = T.describe_transformation(var_name=var_name, apply=apply, groupby=groupby, scaler=scaler)

        fig = plotly_heatmap(
            df,
            height=height,
            width=width,
            #normed_by_cols="normed_by_cols" in options,
            transposed="transposed" in options,
            clustered="clustered" in options,
            add_dendrogram="add_dendrogram" in options,
            correlation="correlation" in options,
            call_show="call_show" in options,
            name=desc,
        )

        return fig
