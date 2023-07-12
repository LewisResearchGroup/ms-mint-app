from pathlib import Path as P

from dash import html, dcc
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State

import plotly.express as px

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt 
import contextlib

from ms_mint import Mint

from .. import tools as T
from ..plugin_interface import PluginInterface


class QualityControlPlugin(PluginInterface):
    def __init__(self):
        self._label = _label
        self._order = 8

    def layout(self):
        return _layout

    def callbacks(self, app, fsc, cache):
        callbacks(app, fsc, cache)
    
    def outputs(self):
        return _outputs
    

_label = "Quality Control"

_layout = html.Div([
    html.H1('Quality Control'),
    html.H2('m/z drift'),
    html.H3('Overall'),
    dcc.Loading(
        dcc.Graph(
            id="qc-fig-mz-drift-overall",
            style={
                "margin": "auto",
                "marginTop": "10%",
                "text-align": "center",
                "maxWidth": "900px",
            },
        ),
    ),
    html.H4('By target'),
    dcc.Loading(
        dcc.Graph(
            id="qc-fig-mz-drift-by-target",
            style={
                "margin": "auto",
                "marginTop": "10%",
                "text-align": "center",
                "maxWidth": "100%",
            },
        )
    ),

    html.H3('PCA'),
    dcc.Loading(
        html.Div(

            dcc.Graph(
                id="qc-fig-pca",
                style={
                    "margin": "auto",
                    "marginTop": "10%",
                    "text-align": "center",
                    "maxWidth": "100%",
                    "minWidth": "100%",
                },
            ),
            style={'width': '50%', 'margin': 'auto'}
        ),
    ),       
    
    html.H3('Peak shapes'),
    dcc.Loading(
        html.Div(
            dcc.Graph(
                id="qc-fig-peak-shapes",
                style={
                    "margin": "auto",
                    "marginTop": "10%",
                    "text-align": "center",
                    "maxWidth": "100%",
                    
                },
            ),
            style={'width': '100%', 'margin': 'auto'}
        ),
    ),    
], style={'width': '100%', "text-align": "left"})

_outputs = html.Div()

def callbacks(app, fsc, cache):
    @app.callback(
        Output("qc-fig-mz-drift-overall", "figure"),
        Input("tab", "value"),
        State("wdir", "children"),
    )
    def create_mz_drift_by_peak_label_overall(
        tab,
        wdir,
    ):
        if tab != "Quality Control":
            raise PreventUpdate
        
        df = T.get_complete_results(
            wdir
        )

        return px.violin(data_frame=df, y='peak_mass_diff_50pc', color='sample_type')
        
    
    @app.callback(
        Output("qc-fig-mz-drift-by-target", "figure"),
        Input("tab", "value"),
        State("wdir", "children"),
    )
    def create_mz_drift_by_peak_label(
        tab,
        wdir,
    ):
        if tab != "Quality Control":
            raise PreventUpdate
        
        df = T.get_complete_results(
            wdir
        )

        fig = px.scatter(data_frame=df, 
                         y='peak_mass_diff_50pc', 
                         x='peak_label',
                         color='sample_type', 
                         hover_data=['ms_file'],
                         #facet_col_wrap=10, 
                         height=750
                )
        fig.update_xaxes(automargin = True)
        return fig


    @app.callback(
        Output("qc-fig-pca", "figure"),
        Input("tab", "value"),
        State("wdir", "children"),
    )
    def create_pca(
        tab,
        wdir,
    ):

        if tab != "Quality Control":
            raise PreventUpdate

        mint = Mint()
        mint.load(T.get_results_fn(wdir))
        mint.load_metadata(T.get_metadata_fn(wdir))

        mint.pca.run(4)

        fig = mint.pca.plot.pairplot(interactive=True, 
                                     hue='sample_type',
                                     height=1000, 
                                     width=1000, 
                                     diag='box')
        return fig


    @app.callback(
        Output("qc-fig-peak-shapes", "figure"),
        Input("tab", "value"),
        State("wdir", "children"),
    )
    def create_peak_shapes(
        tab,
        wdir,
    ):

        if False or (tab != "Quality Control"):
            raise PreventUpdate

        mint = Mint()
        mint.load(T.get_results_fn(wdir))

        # select 30 random files at max
        fns = mint.ms_files
        np.random.shuffle(fns)
        fns = fns[:30]
        fig = mint.plot.peak_shapes(fns=fns, interactive=True, col_wrap=5)
        fig.update_layout(showlegend=True) 
        
        return fig

def layout():
    return _layout