from pathlib import Path as P

from dash import html, dcc
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State

import plotly.express as px

import seaborn as sns
import matplotlib.pyplot as plt 
import contextlib

from ms_mint import Mint

from . import tools as T

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

        return px.violin(data_frame=df, y='peak_mass_diff_50pc', color='Type')
        
    
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
                         color='Type', 
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

        meta = T.get_metadata(wdir).set_index('MS-file')

        mint = Mint()
        mint.load(T.get_results_fn(wdir))
        mint.pca.run(4)

        ndx = mint.pca.results["df_projected"].index.to_list()
        ndx = [P(e).with_suffix('').name for e in ndx]

        labels = list(meta.loc[ndx].Type)


        fig = mint.pca.plot.pairplot(interactive=True, 
                                     labels=labels,
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

        fig = mint.plot.peak_shapes(interactive=True, col_wrap=4)
        fig.update_layout(showlegend=False) 

        return fig

def layout():
    return _layout