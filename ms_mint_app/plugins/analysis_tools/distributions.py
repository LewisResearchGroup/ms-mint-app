from tqdm import tqdm

import matplotlib

matplotlib.use("Agg")
from matplotlib import pyplot as plt
import seaborn as sns

from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State

from ms_mint.Mint import Mint
from ms_mint.standards import MINT_RESULTS_COLUMNS
from ... import tools as T


graph_options = [
    {"label": "Histograms", "value": "hist"},
    {"label": "Boxplots", "value": "boxplot"},
    {"label": "Probability Density", "value": "density"},
]

_label = "Distributions"

_layout = html.Div(
    [
        html.H3("Distributions"),
        dbc.Button("Update", id="dist-update"),
        dcc.Dropdown(
            id="dist-graphs",
            options=graph_options,
            value=["hist"],
            multi=True,
            placeholder="Kinds of graphs",
        ),
        dcc.Checklist(
            id="dist-select",
            options=[{"label": "Dense", "value": "Dense"}],
            value=["Dense"],
        ),
        html.Center(html.H4("", id='description'), style={'marginTop': "200px"}),
        html.Div(id="dist-figures", style={"float": "center"}),
    ]
)


layout_no_data = html.Div(
    [
        dcc.Markdown(
            """### No results generated yet. 
    MINT has not been run yet. The Quality Control tabs uses the processed data. 
    To generate it please add MS-files as well as a valid peaklist. 
    Then execute MINT data processing routine witby clicking the `RUN MINT` button. 
    Once results have been produced you can access the QC tools."""
        ),
    ]
)


def layout():
    return _layout


def callbacks(app, fsc, cache):
    @app.callback(
        Output("dist-figures", "children"),
        Output("description", "children"),
        Input("dist-update", "n_clicks"),
        State("tab", "value"),
        State("ana-var-name", "value"),
        State("ana-colorby", "value"),
        State("ana-groupby", "value"),
        State("ana-scaler", "value"),
        State("ana-apply", "value"),
        State("dist-graphs", "value"),
        State("dist-select", "value"),
        State("ana-file-types", "value"),
        State("ana-peak-labels-include", "value"),
        State("ana-peak-labels-exclude", "value"),
        State("wdir", "children"),
    )
    def qc_figures(
        n_clicks,
        tab,
        var_name,
        colorby,
        groupby,
        scaler,
        apply,
        kinds,
        options,
        file_types,
        include_labels,
        exclude_labels,
        wdir,
    ):

        if n_clicks is None:
            raise PreventUpdate

        df = T.get_complete_results(
            wdir,
            include_labels=include_labels,
            exclude_labels=exclude_labels,
            file_types=file_types,
        )

        mint = Mint()
        mint.results = df[MINT_RESULTS_COLUMNS]
        mint.load_metadata(T.get_metadata_fn(wdir))

        df = mint.crosstab(var_name=var_name, index=['ms_file_label', colorby], 
                           groupby=groupby, apply=apply, scaler=scaler).stack().to_frame().reset_index().rename(columns={0: var_name})

        desc = T.describe_transformation(var_name=var_name, apply=apply, groupby=groupby, scaler=scaler)
        desc_short = desc.split(" (")[0]

        figures = []
        n_total = len(df.peak_label.drop_duplicates())
        for i, (peak_label, grp) in tqdm(
            enumerate(df.groupby("peak_label")), total=n_total
        ):

            if not "Dense" in options:
                figures.append(
                    dcc.Markdown(f"#### `{peak_label}`", style={"float": "center"})
                )
            fsc.set("progress", int(100 * (i + 1) / n_total))

            if "hist" in kinds:
                fig, ax = plt.subplots(figsize=(3, 3))
                
                sns.histplot(data=grp, x=var_name, hue=colorby, ax=ax)
                ax.set_xlabel(desc_short)
                ax.set_title(peak_label)
                fig_label = f"by-{colorby}__{var_name}__{peak_label}"
                #T.savefig(fig, kind="hist", wdir=wdir, label=fig_label)
                src = T.fig_to_src(fig, dpi=150)
                figures.append(html.Img(src=src, style={"width": "300px"}))

            if "density" in kinds:
                # define your figure and axis
                fig, ax = plt.subplots(figsize=(3, 3))

                for label, group_df in grp.groupby(colorby):
                    sns.kdeplot(
                        data=group_df,
                        x=var_name,
                        ax=ax,
                        label=label,
                        common_norm=False,
                    )
                ax.set_xlabel(desc_short)
                ax.set_title(peak_label)
                ax.legend()
                fig_label = f"by-{colorby}__{var_name}__{peak_label}"
                #T.savefig(fig, kind="density", wdir=wdir, label=fig_label)
                src = T.fig_to_src(fig, dpi=150)
                figures.append(html.Img(src=src, style={"width": "300px"}))

            if "boxplot" in kinds:
                n_groups = len(grp[colorby].drop_duplicates())
                aspect = max(1, n_groups / 10)
                
                # define your figure and axis
                fig, ax = plt.subplots(figsize=(aspect*3, 3))

                sns.boxplot(
                    data=grp,
                    y=var_name,
                    x=colorby,
                    color="w",
                    ax=ax
                )

                if var_name in ["peak_max", "peak_area"]:
                    ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
                ax.set_ylabel(desc_short)
                ax.set_title(peak_label)
                plt.xticks(rotation=90)
                fig_label = f"by-{colorby}__{var_name}__{peak_label}"
                #T.savefig(fig, kind="boxplot", wdir=wdir, label=fig_label)
                src = T.fig_to_src(fig, dpi=150)
                figures.append(html.Img(src=src, style={"width": "300px"}))

            if not "Dense" in options:
                figures.append(dcc.Markdown("---"))

        return figures, desc
