from dash import html, dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from ms_mint.standards import RESULTS_COLUMNS

from .analysis_tools import heatmap
from .analysis_tools import pca
from .analysis_tools import distributions
from .analysis_tools import hierachical_clustering
from .analysis_tools import plotting


from .. import tools as T
from ..plugin_interface import PluginInterface



class AnalysisPlugin(PluginInterface):
    def __init__(self):
        self._label = _label
        self._order = 9

    def layout(self):
        return _layout

    def callbacks(self, app, fsc, cache):
        callbacks(app, fsc, cache)
    
    def outputs(self):
        return _outputs
    


_modules = [heatmap, distributions, pca, hierachical_clustering, plotting]

modules = {module._label: module for module in _modules}

colorby_options = [
    {"label": "label", "value": "label"},
    {"label": "plate", "value": "plate"},
    {"label": "sample_type", "value": "sample_type"},
]

apply_options = [{"label": "log10(x+1)", "value": "log1p"}, 
                 {"label": "log2(x+1)" , "value": "log2p1"}]

var_name_options = T.list_to_options(RESULTS_COLUMNS)

scaler_options = [
    {"value": "standard", "label": "Standard scaling (z-scores)"},
    {"value": "minmax", "label": "Min-Max scaling"},
    {"value": "robust", "label": "Robust scaling"}
]


_layout = html.Div(
    [
        dcc.Tabs(
            id="ana-secondary-tab",
            value=_modules[0]._label,
            vertical=False,
            children=[
                dcc.Tab(
                    value=key,
                    label=modules[key]._label,
                )
                for key in modules.keys()
            ],
        ),
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id="ana-file-types",
                    options=[],
                    placeholder="Types of files to include",
                    multi=True,
                ),
                dcc.Dropdown(
                    id="ana-peak-labels-include",
                    options=[],
                    placeholder="Include peak_labels",
                    multi=True,
                ),
                dcc.Dropdown(
                    id="ana-peak-labels-exclude",
                    options=[],
                    placeholder="Exclude peak_labels",
                    multi=True,
                ),
                dcc.Dropdown(
                    id="ana-var-name",
                    options=var_name_options,
                    value='peak_area_top3',
                    placeholder="Variable to plot",
                )
            ]),
            dbc.Col([
                dcc.Dropdown(
                    id="ana-ms-order", options=[], placeholder="MS-file sorting", multi=True
                ),
                dcc.Dropdown(
                    id="ana-colorby",
                    options=colorby_options,
                    value=None,
                    placeholder="Color by",
                ),
                dcc.Dropdown(
                    id="ana-apply",
                    options=apply_options,
                    value=None,
                    placeholder="Transformation",
                    multi=False,
                ),  
                dcc.Dropdown(
                    id="ana-groupby",
                    options=[],
                    value=None,
                    placeholder="Scaling group(s)",
                    multi=True,
                ),
                dcc.Dropdown(
                    id="ana-scaler",
                    options=scaler_options,
                    value=None,
                    placeholder="Scaling method",
                    multi=False,
                ),                                 
            ]),
        ]),
        html.Div(id="ana-secondary-tab-content"),
    ]
)


_label = "Analysis"

_outputs = None


def layout():
    return _layout


def callbacks(app, fsc, cache):

    for module in _modules:
        func = module.callbacks
        if func is not None:
            func(app=app, fsc=fsc, cache=cache)

    @app.callback(
        Output("ana-secondary-tab-content", "children"),
        Input("ana-secondary-tab", "value"),
        State("wdir", "children"),
    )
    def render_content(tab, wdir):
        func = modules[tab].layout
        if func is not None:
            return func()
        else:
            raise PreventUpdate

    @app.callback(
        Output("ana-file-types", "options"),
        Output("ana-file-types", "value"),
        Input("tab", "value"),
        State("wdir", "children"),
    )
    def file_types(tab, wdir):
        if tab != _label:
            raise PreventUpdate
        meta = T.get_metadata(wdir)
        if meta is None:
            raise PreventUpdate
        file_types = meta["sample_type"].drop_duplicates().sort_values()
        options = [{"value": str(i), "label": str(i)} for i in file_types]
        print(file_types, options)
        return options, file_types

    @app.callback(
        Output("ana-ms-order", "options"),
        Output("ana-groupby", "options"),
        Input("ana-secondary-tab", "value"),
        State("wdir", "children"),
    )
    def ms_order_options(tab, wdir):
        cols = T.get_metadata(wdir).dropna(how="all", axis=1).columns.to_list()
        if "index" in cols:
            cols.remove("index")
        if "use_for_optimization" in cols:
            cols.remove("use_for_optimization")
        options_without_peak_label = [{"value": i, "label": i} for i in cols]
        cols.append('peak_label')
        options_with_peak_label = [{"value": i, "label": i} for i in cols]
        return options_without_peak_label, options_with_peak_label

    @app.callback(
        Output("ana-peak-labels-include", "options"),
        Output("ana-peak-labels-exclude", "options"),
        Input("tab", "value"),
        State("wdir", "children"),
    )
    def peak_labels(tab, wdir):
        if tab != _label:
            raise PreventUpdate
        peaklist = T.get_targets(wdir).reset_index()
        options = [{"value": i, "label": i} for i in peaklist.peak_label]
        return options, options
