import os
import shutil
import logging

from tqdm import tqdm

import numpy as np

import matplotlib

matplotlib.use("Agg")
from matplotlib import pyplot as plt
import seaborn as sns

import dash
from dash import html, dcc
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State, ALL

import dash_bootstrap_components as dbc

import plotly.graph_objects as go

from ms_mint import Mint

from . import tools as T


info_txt = """
Creating chromatograms from mzXML/mzML files can last 
a long time the first time. Try converting your files to 
_feather_ format first.'
"""

_label = "Optimization"

_layout = html.Div(
    [
        html.H3("Target Optimization"),
        dcc.Markdown("---"),
        html.H4("File selection"),
        dcc.Dropdown(
            id="pko-ms-selection",
            options=[
                {
                    "label": "Use selected files from metadata table (PeakOpt)",
                    "value": "peakopt",
                },
                {"label": "Use all files (may take a long time)", "value": "all"},
            ],
            value="peakopt",
            clearable=False,
            style={'max-width': '400px'}
        ),

        html.H4("Peak previews"),
        dbc.Row([
            dbc.Col(dbc.Button("Update peak previews", id="pko-peak-preview", style={'width': '100%'})),
            dbc.Col(dbc.Button("Regenerate all figures", id="pko-peak-preview-from-scratch", style={'width': '100%'})),
            dbc.Col(dbc.Button("Detect rt_min,rt_max for all targets", id="pko-detect-rtmin-rtmax-for-all", color='danger', style={'width': '100%'})),
        ]),
        dcc.Markdown("---"),

        html.Div(
            id="pko-peak-preview-images",
            style={"maxHeight": "600px", "overflowX": "scroll", "padding": "auto"},

        ),
        dcc.Markdown("---"),
        html.H4("Interactive Rt optimization"),

        html.Div(id="pko-controls"),
        dcc.Dropdown(id="pko-dropdown", options=[], value=None),
        dbc.Progress(
            id="pko-progress-bar",
            value=0,
            style={"marginBottom": "20px", "width": "100%"},
        ),

        dbc.Row([
            dbc.Col(dbc.Button("Set RT to current view", id="pko-set-rt", style={"width": "100%"})),
            dbc.Col(dbc.Button("Detect rt_min,rt_max", id="pko-detect-rtmin-rtmax", style={"width": "100%"})),
            dbc.Col(dbc.Button("Confirm retention time", id="pko-confirm-rt", style={"width": "100%"})),
            dbc.Col(dbc.Button("Remove Peak", id="pko-delete", style={"width": "100%"}, color='danger')),
        ]),

        dcc.Loading(dcc.Graph("pko-figure")),
        dcc.Checklist(
            id="pko-figure-options",
            options=[{"value": "log", "label": "Logarithmic y-scale"}],
            value=[],
        ),        
        html.Div(id="pko-image-clicked", style={'visibility': 'hidden'}),
        dbc.Row(
            children=[
                dbc.Col(dbc.Button("<< Previous", id="pko-prev", style={'width': '100%'})),
                dbc.Col(dbc.Button("Suggest", id="pko-suggest-next", style={'width': '100%'})),
                dbc.Col(dbc.Button("Next >>", id="pko-next", style={'width': '100%'})),
            ],
            style={"text-align": "center", "margin": "auto", "marginTop": "2%"},
        ),
    ]
)


pko_layout_no_data = html.Div(
    [
        dcc.Markdown(
            """### No targets found.
    You did not generate a targets yet.
    """
        )
    ]
)


_outputs = html.Div(
    id="pko-outputs",
    children=[
        html.Div(id={"index": "pko-set-rt-output", "type": "output"}),
        html.Div(id={"index": "pko-confirm-rt-output", "type": "output"}),
        html.Div(
            id={"index": "pko-detect-rtmin-rtmax-for-all-output", "type": "output"}
        ),
        html.Div(id={"index": "pko-detect-rtmin-rtmax-output", "type": "output"}),
        html.Div(id={"index": "pko-delete-output", "type": "output"}),
        html.Div(id={"index": "pko-remove-low-intensity-output", "type": "output"}),
    ],
)


def layout():
    return _layout


def callbacks(app, fsc, cache, cpu=None):
    @app.callback(
        Output("pko-dropdown", "options"),
        Input("tab", "value"),
        Input({"index": "pko-delete-output", "type": "output"}, "children"),
        State("wdir", "children"),
        State("pko-dropdown", "options"),
    )
    def pko_controls(tab, peak_deleted, wdir, old_options):
        if tab != _label:
            raise PreventUpdate
        targets = T.get_targets(wdir)
        if targets is None:
            logging.warning("Target-list is empty")
            raise PreventUpdate
        options = [
            {"label": label, "value": i} for i, label in enumerate(targets.index)
        ]
        if options == old_options:
            raise PreventUpdate
        return options

    @app.callback(
        Output("pko-figure", "figure"),
        Input("pko-dropdown", "value"),
        Input("pko-figure-options", "value"),
        Input({"index": "pko-set-rt-output", "type": "output"}, "children"),
        Input("pko-dropdown", "options"),
        Input(
            {"index": "pko-detect-rtmin-rtmax-for-all-output", "type": "output"},
            "children",
        ),
        Input({"index": "pko-detect-rtmin-rtmax-output", "type": "output"}, "children"),
        Input({"index": "pko-confirm-rt-output", "type": "output"}, "children"),
        State("pko-ms-selection", "value"),
        State("wdir", "children"),
    )
    def pko_figure(
        peak_label_ndx,
        options,
        n_clicks,
        options_changed,
        find_largest_peak,
        find_largest_peak_single,
        rt_set,
        ms_selection,
        wdir,
    ):
        fig = None
        if peak_label_ndx is None:
            raise PreventUpdate
        targets = T.get_targets(wdir).reset_index()
        if ms_selection == "peakopt":
            ms_files = T.get_ms_fns_for_peakopt(wdir)
        elif ms_selection == "all":
            ms_files = T.get_ms_fns(wdir)

        cols = ["mz_mean", "mz_width", "rt", "rt_min", "rt_max", "peak_label"]

        peak_label_ndx = peak_label_ndx % len(targets)
        mz_mean, mz_width, rt, rt_min, rt_max, label = targets.loc[peak_label_ndx, cols]
        margin = 30
        if rt is np.isnan(rt):
            if (not np.isnan(rt_min)) and (not np.isnan(rt_max)):
                rt = np.mean([rt_min, rt_max])
        else:
            if (rt_min is None) or np.isnan(rt_min):
                rt_min = max(0, rt - margin)
            if (rt_max is None) or np.isnan(rt_max):
                rt_max = rt + margin

        if True or fig is None:
            fig = go.Figure()
            fig.layout.hovermode = "closest"
            fig.layout.xaxis.range = [rt_min, rt_max]

            fig.update_layout(
                yaxis_title="Intensity",
                xaxis_title="Scan Time [s]",
                xaxis=dict(rangeslider=dict(visible=True)),
            )
            fig.update_layout(title=label)
            if "log" in options:
                fig.update_yaxes(type="log")

        if not np.isnan(rt):
            fig.add_vline(rt)

        if (not np.isnan(rt_min)) and (not np.isnan(rt_max)):
            fig.add_vrect(
                x0=rt_min, x1=rt_max, line_width=0, fillcolor="green", opacity=0.1
            )

        n_files = len(ms_files)
        for i, fn in tqdm(enumerate(ms_files), total=n_files, desc="PKO-figure"):
            fsc.set("progress", int(100 * (i + 1) / n_files))

            name = os.path.basename(fn)
            name, _ = os.path.splitext(name)
            chrom = T.get_chromatogram(fn, mz_mean, mz_width, wdir)
            fig.add_trace(
                go.Scatter(x=chrom["scan_time"], y=chrom["intensity"], name=name)
            )
            fig.update_layout(showlegend=False)
            fig.update_layout(hoverlabel=dict(namelength=-1))
        return fig

    @app.callback(
        Output("pko-progress-bar", "value"),
        Input("pko-dropdown", "value"),
        State("pko-dropdown", "options"),
    )
    def set_progress(value, options):
        if (value is None) or (options is None):
            raise PreventUpdate
        progress = int(100 * (value + 1) / len(options))
        return progress

    @app.callback(
        Output({"index": "pko-detect-rtmin-rtmax-for-all-output", "type": "output"}, "children"),
        Input("pko-detect-rtmin-rtmax-for-all", "n_clicks"),
        State("pko-ms-selection", "value"),
        State("wdir", "children"),
    )
    def pko_optimise_rt_min_ma_for_all_targets(n_clicks, ms_selection, wdir):
        if n_clicks is None:
            raise PreventUpdate

        logging.warning(f'Running peak detection {wdir}')

        targets = T.get_targets(wdir)

        if ms_selection == "peakopt":
            ms_files = T.get_ms_fns_for_peakopt(wdir)

        elif ms_selection == "all":
            ms_files = T.get_ms_fns(wdir)

        mint = Mint()
        mint.targets = targets.reset_index()
        mint.ms_files = ms_files
        mint.opt.rt_min_max()       
        new_targets = mint.targets

        T.write_targets(new_targets, wdir)

        return dbc.Alert("Rt detection finished.", color="success")

    @app.callback(
        Output({"index": "pko-set-rt-output", "type": "output"}, "children"),
        Input("pko-set-rt", "n_clicks"),
        State("pko-dropdown", "value"),
        State("pko-figure", "figure"),
        State("wdir", "children"),
    )
    def pko_set_rt_min_max(n_clicks, peak_label, fig, wdir):
        if n_clicks is None:
            raise PreventUpdate
        rt_min, rt_max = fig["layout"]["xaxis"]["range"]
        rt_min, rt_max = np.round(rt_min, 4), np.round(rt_max, 4)
        T.update_targets(wdir, peak_label, rt_min, rt_max)
        return dbc.Alert(f"Set RT span to ({rt_min},{rt_max})", color="info")

    @app.callback(
        Output({"index": "pko-confirm-rt-output", "type": "output"}, "children"),
        Input("pko-confirm-rt", "n_clicks"),
        State("pko-dropdown", "value"),
        State("pko-figure", "figure"),
        State("wdir", "children"),
    )
    def pko_confirm_rt(n_clicks, peak_label, fig, wdir):
        if n_clicks is None:
            raise PreventUpdate

        rt_min, rt_max = fig["layout"]["xaxis"]["range"]
        rt_min, rt_max = np.round(rt_min, 4), np.round(rt_max, 4)

        image_label = f"{peak_label}_{rt_min}_{rt_max}"

        _, fn = T.get_figure_fn(
            kind="peak-preview", wdir=wdir, label=image_label, format="png"
        )

        rt = np.mean([rt_min, rt_max])

        T.update_targets(wdir, peak_label, rt=rt)

        if os.path.isfile(fn):
            os.remove(fn)

        return dbc.Alert(f"Set RT span to ({rt_min},{rt_max})", color="info")

    @app.callback(
        Output("pko-dropdown", "value"),
        Input("pko-prev", "n_clicks"),
        Input("pko-suggest-next", "n_clicks"),
        Input("pko-next", "n_clicks"),
        Input("pko-image-clicked", "children"),
        State("pko-dropdown", "value"),
        State("pko-dropdown", "options"),
        State("wdir", "children"),
    )
    def pko_prev_next_suggest(
        n_prev, n_suggest, n_next, image_clicked, value, options, wdir
    ):
        if (
            n_prev is None
            and n_next is None
            and image_clicked is None
            and n_suggest is None
        ):
            raise PreventUpdate

        prop_id = dash.callback_context.triggered[0]["prop_id"]

        if prop_id.startswith("pko-suggest"):

            targets = T.get_targets(wdir).reset_index()

            # If targets have missing values in RT columns
            # return index of first target with missing value
            if T.has_na(targets[["rt_min", "rt_max"]]):
                ndx_na_rt_min = targets[targets["rt_min"].isna()].index.to_list()
                ndx_na_rt_max = targets[targets["rt_max"].isna()].index.to_list()
                return min(ndx_na_rt_min + ndx_na_rt_max)

            rt_means = targets[["rt_min", "rt_max"]].mean(axis=1)

            peak_label_ndx = np.argmax((targets.rt - rt_means).abs())

            return peak_label_ndx

        if prop_id.startswith("pko-image-clicked"):
            for entry in options:
                if entry["label"] == image_clicked:
                    return entry["value"]
        elif value is None:
            return 0
        elif prop_id.startswith("pko-prev"):
            return (value - 1) % len(options)
        elif prop_id.startswith("pko-next"):
            return (value + 1) % len(options)

    @app.callback(
        Output("pko-peak-preview-images", "children"),
        Input("pko-peak-preview", "n_clicks"),
        Input("pko-peak-preview-from-scratch", "n_clicks"),
        State("pko-ms-selection", "value"),
        State("wdir", "children"),
    )
    def peak_preview(n_clicks, from_scratch, ms_selection, wdir):  # peak_opt, #set_rt,
        logging.warning(f'Create peak previews {wdir}')
        if n_clicks is None:
            raise PreventUpdate
        # reset updating after 5 attempts
        n_attempts = fsc.get(f"{wdir}-update-attempt")
        if n_attempts is None:
            n_attempts = 1
        elif n_attempts % 5:
            fsc.set(f"{wdir}-updating", False)

        # increment counter of attempts
        fsc.set(f"{wdir}-update-attempt", n_attempts + 1)

        if fsc.get(f"{wdir}-updating") is True:
            raise PreventUpdate

        fsc.set(f"{wdir}-updating", True)

        prop_id = dash.callback_context.triggered[0]["prop_id"]
        regenerate = prop_id.startswith("pko-peak-preview-from-scratch")
        if regenerate:
            image_path = os.path.join(wdir, "figures", "peak-preview")
            if os.path.isdir(image_path):
                shutil.rmtree(image_path)

        if ms_selection == "peakopt":
            ms_files = T.get_ms_fns_for_peakopt(wdir)
        elif ms_selection == "all":
            ms_files = T.get_ms_fns(wdir)
        else:
            assert False, ms_selection

        if len(ms_files) == 0:
            return dbc.Alert(
                'No files selected for peak optimization in Metadata tab. Please, select some files in column "PeakOpt".',
                color="warning",
            )
        else:
            logging.info(
                f"Using {len(ms_files)} files for peak preview. ({ms_selection})"
            )

        targets = T.get_targets(wdir)

        file_colors = T.file_colors(wdir)

        n_total = len(targets)

        sns.set_context("paper")
        images = []
        for i, (peak_label, row) in tqdm(enumerate(targets.iterrows()), total=n_total):
            fsc.set("progress", int(100 * (i + 1) / n_total))
            mz_mean, mz_width, rt, rt_min, rt_max = row[
                ["mz_mean", "mz_width", "rt", "rt_min", "rt_max"]
            ]

            if rt_min is None or np.isnan(rt_min):
                rt_min = 0
            if  rt_max is None or np.isnan(rt_max):
                rt_max = 1000

            image_label = f"{peak_label}_{rt_min}_{rt_max}"

            _, fn = T.get_figure_fn(
                kind="peak-preview", wdir=wdir, label=image_label, format="png"
            )

            if not os.path.isfile(fn) or regenerate:
                logging.info(f"Regenerating figure for {peak_label}")
                create_preview_peakshape(
                    ms_files,
                    mz_mean,
                    mz_width,
                    rt,
                    rt_min,
                    rt_max,
                    image_label,
                    wdir,
                    peak_label=peak_label,
                    colors=file_colors,
                )

            if os.path.isfile(fn):
                src = T.png_fn_to_src(fn)
            else:
                src = None

            _id = {"index": peak_label, "type": "image"}
            image_id = f"image-{i}"
            images.append(
                html.A(
                    id=_id,
                    children=html.Img(
                        src=src, height=300, id=image_id, style={"margin": "10px"}
                    ),
                )
            )
            images.append(
                dbc.Tooltip(peak_label, target=image_id, style={"font-size": "50"})
            )
        fsc.set(f"{wdir}-updating", False)
        return images

    @app.callback(
        Output("pko-image-clicked", "children"),
        # Input needs brakets to make prevent_initital_call work
        [Input({"type": "image", "index": ALL}, "n_clicks")],
        prevent_initial_call=True,
    )
    def pko_image_clicked(ndx):
        if ndx is None or len(ndx) == 0:
            raise PreventUpdate
        ctx = dash.callback_context
        clicked = ctx.triggered[0]["prop_id"]
        clicked = clicked.replace('{"index":"', "")
        clicked = clicked.split('","type":')[0].replace("\\", "")
        if len(dash.callback_context.triggered) > 1:
            raise PreventUpdate
        return clicked

    @app.callback(
        Output({"index": "pko-delete-output", "type": "output"}, "children"),
        Input("pko-delete", "n_clicks"),
        State("pko-dropdown", "value"),
        State("wdir", "children"),
    )
    def plk_delete(n_clicks, peak_ndx, wdir):
        if n_clicks is None:
            raise PreventUpdate
        targets = T.get_targets(wdir).reset_index()
        peak_label = targets.loc[peak_ndx, "peak_label"]
        targets = targets.drop(peak_ndx, axis=0)
        T.write_targets(targets, wdir)
        return dbc.Alert(f"{peak_label} removed from targets.", color="info")

    @app.callback(
        Output({"index": "pko-detect-rtmin-rtmax-output", "type": "output"}, "children"),
        Input("pko-detect-rtmin-rtmax", "n_clicks"),
        State("pko-dropdown", "value"),
        State("pko-ms-selection", "value"),
        State("wdir", "children"),
    )
    def detect_rt_min_max(n_clicks, peak_label_ndx, ms_selection, wdir):
        if n_clicks is None:
            raise PreventUpdate
        if peak_label_ndx is None:
            raise PreventUpdate
        targets = T.get_targets(wdir).reset_index()

        if ms_selection == "peakopt":
            ms_files = T.get_ms_fns_for_peakopt(wdir)
        elif ms_selection == "all":
            ms_files = T.get_ms_fns(wdir)

        peak_label = targets.at[peak_label_ndx, 'peak_label']
        
        mint = Mint()
        mint.targets = targets
        mint.ms_files = ms_files
        mint.opt.find_rt_min_max(peak_labels=[peak_label])       
        new_targets = mint.targets
        new_targets.to_csv(T.get_targets_fn(wdir), index=False)

        return dbc.Alert(
            f"Done optimize rt_min rt_max for {peak_label}", color="info"
        )
        

def create_preview_peakshape(
    ms_files, mz_mean, mz_width, rt, rt_min, rt_max, image_label, wdir, peak_label, colors
):
    """Create peak shape previews."""
    plt.figure(figsize=(2, 1), dpi=30)
    y_max = 0
    for fn in ms_files:
        color = colors[T.filename_to_label(fn)]
        if color is None or color == "":
            color = "grey"
        fn_chro = T.get_chromatogram(fn, mz_mean, mz_width, wdir)
        fn_chro = fn_chro[
            (rt_min < fn_chro["scan_time"]) & (fn_chro["scan_time"] < rt_max)
        ]
        plt.plot(fn_chro["scan_time"], fn_chro["intensity"], lw=1, color=color)
        y_max = max(y_max, fn_chro["intensity"].max())
    if (not np.isnan(rt)) and not (np.isnan(rt_max)) and not (np.isnan(rt_min)):
        x = max(min(rt, rt_max), rt_min)
        rt_mean = np.mean([rt_min, rt_max])
        color_value = np.abs(rt_mean - rt) / 10
        color = T.float_to_color(color_value, vmin=0, vmax=1, cmap="coolwarm")
        plt.vlines(x, 0, y_max, lw=3, color=color)
    title = f'{peak_label[:30]}\nm/z={mz_mean:.2f}'
    plt.gca().set_title(title, y=1.0, pad=15)
    plt.gca().ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
    plt.xlabel("Scan Time [s]")
    plt.ylabel("Intensity")
    filename = T.savefig(kind="peak-preview", wdir=wdir, label=image_label)
    plt.close()
    return filename
