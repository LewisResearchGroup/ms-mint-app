import numpy as np
import seaborn as sns
import plotly.express as px

from dash import html, dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import dash_bootstrap_components as dbc

from ms_mint import Mint

from ... import tools as T

options = [{"value": i, "label": i} for i in ["Standard scaling", "Corner"]]

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
        State("ana-groupby", "value"),
        State("ana-peak-labels-include", "value"),
        State("ana-peak-labels-exclude", "value"),
        State("ana-normalization-cols", "value"),
        State("ana-file-types", "value"),
        State("pca-options", "value"),
        State("wdir", "children"),
    )
    def create_pca(
        n_clicks,
        n_components,
        groupby,
        include_labels,
        exclude_labels,
        norm_cols,
        file_types,
        options,
        wdir,
    ):
        if n_clicks is None:
            raise PreventUpdate
        if norm_cols is None:
            norm_cols = []

        df = T.get_complete_results(
            wdir,
            include_labels=include_labels,
            exclude_labels=exclude_labels,
            file_types=file_types,
        )

        if file_types is not None and len(file_types) > 0:
            df = df[df["sample_type"].isin(file_types)]

        if groupby is not None and len(groupby) > 0:
            labels = (
                df[["ms_file_label", groupby]].drop_duplicates().set_index("ms_file_label")
            )
        else:
            labels = None
            groupby = None

        if len(norm_cols) != 0:
            if ("peak_label" in norm_cols) and ("ms_file" in norm_cols):
                return dbc.Alert(
                    "'peak_label' and 'ms_file' should not be used together for normalization!",
                    color="danger",
                )

            df = df[df.Batch.notna()]
            cols = ["peak_max"]
            df.loc[:, cols] = (
                (
                    df[cols]
                    - df[cols + norm_cols]
                    .groupby(norm_cols)
                    .transform("median")[cols]
                    .values
                )
                / df[cols + norm_cols].groupby(norm_cols).transform("std")[cols].values
            ).reset_index()

        figures = []
        mint = Mint()
        mint.results = df
        mint.load_metadata(T.get_metadata_fn(wdir))

        mint.pca.run(n_components=n_components)

        fig_scattermatrix = mint.pca.plot.pairplot(
                n_components=n_components,
                hue=groupby,
                interactive=True,
                height=n_components*200+100,
                width=n_components*200+100,
                title='Principal components scatter plot',
                diag='box'
            )

        fig_cumvar = mint.pca.plot.cumulative_variance(interactive=True, width=n_components*20+500)

        fig_contrib = mint.pca.plot.loadings(interactive=True, 
                                             height=n_components*200+100, 
                                             width=len(mint.targets)*20+500,
                                             title='Principal component loadings')

        fig_scattermatrix.update_layout(autosize=True)
        fig_cumvar.update_layout(autosize=True)        
        fig_contrib.update_layout(autosize=True)

        return fig_scattermatrix, fig_cumvar, fig_contrib
