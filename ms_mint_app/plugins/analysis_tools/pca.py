import logging

import numpy as np
import seaborn as sns
import plotly.express as px

from dash import html, dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import dash_bootstrap_components as dbc

from ms_mint import Mint
from ms_mint.standards import MINT_RESULTS_COLUMNS

from ... import tools as T

options = []

_layout = html.Div(
    [
        html.H3("Principal Components Analysis"),
        dbc.Button("Run PCA", id="pca-update"),
        dcc.Dropdown(
            id="pca-options",
            options=options,
            value=["Standard scaling"],
            multi=True,
            placeholder="Scaling used before PCA",
        ),

        html.Label("Number of PCA components"),
        dcc.Slider(
            id="pca-nvars",
            value=3,
            min=2,
            max=10,
            step=1,
            marks={i: f"{i}" for i in range(2, 11)},
        ),

        html.H4("Scatter plot of principal components"),
        html.Center([
            dcc.Loading(
                dcc.Graph(
                    id="pca-figure-pairplot",
                )
            ),
        ]),

        html.H4("Cumulative explained variance"),
        html.Center([
            dcc.Loading(
                dcc.Graph(
                    id="pca-figure-explained-variance",
                )
            ),
        ]),
    
        html.H4("PCA-Loadings"),
        html.Center([
            dcc.Loading(dcc.Graph(id="pca-figure-contrib")),
        ]),
    ]
)

_label = "PCA"


def layout():
    return _layout


def callbacks(app, fsc, cache):
    @app.callback(
        Output("pca-figure-pairplot", "figure"),
        Output("pca-figure-explained-variance", "figure"),
        Output("pca-figure-contrib", "figure"),
        Input("pca-update", "n_clicks"),
        State("pca-nvars", "value"),
        State("ana-var-name", "value"),
        State("ana-colorby", "value"),
        State("ana-groupby", "value"),
        State("ana-scaler", "value"),
        State("ana-apply", "value"),
        State("ana-peak-labels-include", "value"),
        State("ana-peak-labels-exclude", "value"),
        State("ana-file-types", "value"),
        State("pca-options", "value"),
        State("viewport-container", "children"),
        State("wdir", "children"),
    )
    def create_pca(
        n_clicks,
        n_components,
        var_name,
        colorby,
        groupby,
        scaler,
        apply,
        include_labels,
        exclude_labels,
        file_types,
        options,
        viewport,
        wdir,
    ):
        
        width, height = [int(e) for e in viewport.split(",")]

        if n_clicks is None:
            raise PreventUpdate
        if groupby is None:
            groupby = []

        df = T.get_complete_results(
            wdir,
            include_labels=include_labels,
            exclude_labels=exclude_labels,
            file_types=file_types,
        )

        figures = []
        mint = Mint()
        mint.results = df[MINT_RESULTS_COLUMNS]
        mint.load_metadata(T.get_metadata_fn(wdir))

        n_peak_labels = len(mint.results.peak_label.drop_duplicates())

        desc = T.describe_transformation(var_name=var_name, apply=apply, groupby=groupby, scaler=scaler)
        desc_short = desc.split(" (")[0]

        try:
            mint.pca.run(var_name=var_name, n_components=n_components, groupby=groupby, scaler=scaler, apply=apply)
        except RuntimeWarning as e:
            logging.error(e)
            return dbc.Alert(str(e), color="warning")

        fig_scattermatrix = mint.pca.plot.pairplot(
                n_components=n_components,
                hue=colorby,
                interactive=True,
                height=min(n_components*200+100, width),
                width=min(n_components*200+100, width),
                title=f'Principal components scatter plot ({var_name})',
                diag='box'
            )

        fig_cumvar = mint.pca.plot.cumulative_variance(interactive=True, width=min(n_components*20+500, width))

        fig_contrib = mint.pca.plot.loadings(interactive=True, 
                                             height=n_components*200+100, 
                                             width=min(n_peak_labels*50+350, width),
                                             title=f'Principal component loadings ({var_name})')

        fig_scattermatrix.update_layout(autosize=True)
        fig_cumvar.update_layout(autosize=True)        
        fig_contrib.update_layout(autosize=True)

        return fig_scattermatrix, fig_cumvar, fig_contrib
