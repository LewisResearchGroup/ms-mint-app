import os

from pathlib import Path as P

import dash
from dash import html

import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from dash.dcc import send_file, send_bytes

from dash.dependencies import Input, Output, State

from ms_mint.Mint import Mint

from . import tools as T

_label = "Processing"


_layout = html.Div(
    [
        html.H3("Run MINT"),
        dbc.Row([
            dbc.Col(dbc.Button("Run MINT", id="run-mint", style={"width": "100%"})),
            dbc.Col(dbc.Button("Download all results", id="res-download", style={"width": "100%"}, color='secondary')),
            dbc.Col(dbc.Button("Download dense peak_max", id="res-download-peakmax", style={"width": "100%"}, color='secondary')),
            dbc.Col(dbc.Button("Delete results", id="res-delete", style={"width": "100%"}, color='danger')),
        ])
    ]
)

_outputs = html.Div(
    id="run-outputs",
    children=[
        html.Div(
            id={"index": "run-mint-output", "type": "output"},
            style={"visibility": "hidden"},
        ),
        html.Div(
            id={"index": "res-delete-output", "type": "output"},
            style={"visibility": "hidden"},
        ),
    ],
)


def layout():
    return _layout


def callbacks(app, fsc, cache):
    @app.callback(
        Output({"index": "res-delete-output", "type": "output"}, "children"),
        Input("res-delete", "n_clicks"),
        State("wdir", "children"),
    )
    def heat_delete(n_clicks, wdir):
        if n_clicks is None:
            raise PreventUpdate
        os.remove(T.get_results_fn(wdir))
        return dbc.Alert("Results file deleted.", color='success')

    @app.callback(
        [
            Output("res-download-data", "data"),
            Input("res-download", "n_clicks"),
            Input("res-download-peakmax", "n_clicks"),
            State("wdir", "children"),
        ]
    )
    def download_results(n_clicks, n_clicks_peakmax, wdir):
        if (n_clicks is None) and (n_clicks_peakmax is None):
            raise PreventUpdate
        ctx = dash.callback_context

        prop_id = ctx.triggered[0]["prop_id"]

        if prop_id == "res-download.n_clicks":
            fn = T.get_results_fn(wdir)
            workspace = os.path.basename(wdir)
            return [
                send_file(fn, filename=f"{T.today()}-MINT__{workspace}__results.csv")
            ]

        elif prop_id == "res-download-peakmax.n_clicks":
            workspace = os.path.basename(wdir)
            results = T.get_results(wdir)
            df = results.pivot_table("peak_max", "peak_label", "ms_file")
            df.columns = [P(x).with_suffix("") for x in df.columns]
            buffer = T.df_to_in_memory_excel_file(df)
            return [
                send_bytes(
                    buffer, filename=f"{T.today()}-MINT__{workspace}__results_peak-max.xlsx"
                )
            ]

    @app.callback(
        Output({"index": "run-mint-output", "type": "output"}, "children"),
        Input("run-mint", "n_clicks"),
        State("wdir", "children"),
    )
    def run_mint(n_clicks, wdir):
        if n_clicks is None:
            raise PreventUpdate

        def set_progress(x):
            fsc.set("progress", x)

        mint = Mint(verbose=False, progress_callback=set_progress)
        targets_fn = T.get_targets_fn(wdir)
        output_fn = T.get_results_fn(wdir)
        try:
            mint.load_targets(targets_fn)
            mint.ms_files = T.get_ms_fns(wdir)
            mint.run(fn=output_fn)
        except Exception as e:
            return dbc.Alert(str(e), color="danger")
        return dbc.Alert("Finished running MINT", color="success")
