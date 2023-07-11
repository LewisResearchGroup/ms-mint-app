import os
import tempfile
import logging
import importlib

import pandas as pd

from pathlib import Path as P

import matplotlib

matplotlib.use("Agg")

import dash

from dash import html, dcc

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash.dcc import Download
from dash_extensions.enrich import FileSystemCache
from dash.long_callback import DiskcacheLongCallbackManager

from .plugin_manager import PluginManager
from .plugin_interface import PluginInterface

import dash_bootstrap_components as dbc

from flask_caching import Cache
from flask_login import current_user

import ms_mint
import ms_mint_app

from . import tools as T
from . import messages

import dash_uploader as du


def make_dirs():
    tmpdir = tempfile.gettempdir()
    tmpdir = os.path.join(tmpdir, "MINT")
    tmpdir = os.getenv("MINT_DATA_DIR", default=tmpdir)
    cachedir = os.path.join(tmpdir, ".cache")
    os.makedirs(tmpdir, exist_ok=True)
    os.makedirs(cachedir, exist_ok=True)
    print("MAKEDIRS:", tmpdir, cachedir)
    return P(tmpdir), P(cachedir)


TMPDIR, CACHEDIR = make_dirs()

config = {
    "DEBUG": True,  # some Flask specific configs
    "CACHE_TYPE": "simple",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300,
}

logging.info(f'CACHEDIR: {CACHEDIR}')
logging.info(f'TMPDIR: {TMPDIR}')

## Diskcache
from uuid import uuid4
import diskcache
launch_uid = uuid4()
cache = diskcache.Cache(CACHEDIR)
long_callback_manager = DiskcacheLongCallbackManager(
    cache, cache_by=[lambda: launch_uid], expire=60,
)

pd.options.display.max_colwidth = 1000


def load_plugins(plugin_dir, package_name):
    logging.info('Loading plugins')
    plugins = {}

    for file in os.listdir(plugin_dir):
        if file.endswith(".py") and not file.startswith("__"):
            module_name = file[:-3]
            module_path = f"{package_name}.{module_name}"
            module = importlib.import_module(module_path)

            for name, cls in module.__dict__.items():
                if isinstance(cls, type) and issubclass(cls, PluginInterface) and cls is not PluginInterface:
                    plugin_instance = cls()
                    plugins[plugin_instance.label] = plugin_instance

    return plugins

# Assuming 'plugins' is a subdirectory in the same directory as this script
plugin_manager = PluginManager()
plugins = plugin_manager.get_plugins()

logging.info(f'Plugins: {plugins.keys()}')

# Collect outputs:
_outputs = html.Div(
    id="outputs",
    children=[plugin.outputs() for plugin in plugins.values() if plugin.outputs is not None],
    style={"visibility": "hidden"},
)

#logging.info(f'Outputs: {_outputs}')

logout_button = (
    dbc.Button(
        "Logout",
        id="logout-button",
        style={"marginRight": "10px", "visibility": "hidden"},
    ),
)
logout_button = html.A(href="/logout", children=logout_button)

_layout = html.Div(
    [
        html.Div(logout_button),
        dcc.Interval(
            id="progress-interval", n_intervals=0, interval=2000, disabled=False
        ),
        html.A(
            href="https://lewisresearchgroup.github.io/ms-mint-app/gui/",
            children=[
                html.Button(
                    "Documentation",
                    id="B_help",
                    style={"float": "right", "color": "info"},
                )
            ],
            target="_blank",
        ),
        html.A(
            href=f"https://github.com/LewisResearchGroup/ms-mint-app/issues/new?body={T.get_issue_text()}",
            children=[
                html.Button(
                    "Issues", id="B_issues", style={"float": "right", "color": "info"}
                )
            ],
            target="_blank",
        ),
        dbc.Progress(
            id="progress-bar",
            value=100,
            style={"marginBottom": "20px", "width": "100%", "marginTop": "20px"},
        ),
        Download(id="res-download-data"),
        html.Div(id="tmpdir", children=str(TMPDIR), style={"visibility": "hidden"}),

        dbc.Row([
            dbc.Col(
                dbc.Alert(
                    [
                        html.H6("Workspace: ", style={"display": "inline"}),
                        html.H6(id="active-workspace", style={"display": "inline"}),
                    ]
                , color='info', style={'text-align': 'center'}),
            ),
            dbc.Col(
                dbc.Alert(
                    [
                        html.H6(id="wdir", style={"display": "inline"}),
                    ]
                , color='info', style={'text-align': 'center'}),
            ),
        ], style={'marginTop': '5px', "marginBottom": "30px"}),

        html.Div(id="pko-creating-chromatograms"),

        dcc.Tabs(
            id="tab",
            value=list(plugins.keys())[0],
            children=[
                dcc.Tab(
                    id=plugin_id,
                    value=plugin_id,
                    label=plugin_instance.label,
                )
                for plugin_id, plugin_instance in plugins.items()
            ],
        ),

        messages.layout(),

        html.Div(id="pko-image-store", style={"visibility": "hidden", "height": "0px"}),
        html.Div(id="tab-content"),
        html.Div(id="viewport-container", style={"visibility": "hidden"}),
        _outputs,
        html.Div(f'ms-mint: {ms_mint.__version__}'),
        html.Div(f'ms-mint-app: {ms_mint_app.__version__}'),
    ],
    style={"margin": "2%"},

)


def register_callbacks(app, cache, fsc):
    logging.info("Register callbacks")
    upload_root = os.getenv("MINT_DATA_DIR", tempfile.gettempdir())
    upload_dir = str(P(upload_root) / "MINT-Uploads")
    UPLOAD_FOLDER_ROOT = upload_dir
    du.configure_upload(app, UPLOAD_FOLDER_ROOT)

    messages.callbacks(app=app, fsc=fsc, cache=cache)

    for label, plugin in plugins.items():
        logging.info(f"Loading callbacks of plugin {label}")
        plugin.callbacks(app=app, fsc=fsc, cache=cache)

    logging.info(f"Define clientside callbacks")
    # Updates the current viewport
    app.clientside_callback(
        """
        function(href) {
            var w = window.innerWidth;
            var h = window.innerHeight;
            return `${w},${h}` ;
        }
        """,
        Output("viewport-container", "children"),
        Input("progress-interval", "n_intervals"),
    )

    @app.callback(
        Output("tab-content", "children"),
        Input("tab", "value"),
        State("wdir", "children"),
    )
    def render_content(tab, wdir):
        func = plugins[tab].layout
        if tab != "Workspaces" and wdir == "":
            return dbc.Alert(
                "Please, create and activate a workspace.", color="warning"
            )
        elif (
            tab in ["Metadata", "Peak Optimization", "Processing"]
            and len(T.get_ms_fns(wdir)) == 0
        ):
            return dbc.Alert("Please import MS files.", color="warning")
        elif tab in ["Processing"] and (len(T.get_targets(wdir)) == 0):
            return dbc.Alert("Please, define targets.", color="warning")
        elif tab in ["Analysis"] and not P(T.get_results_fn(wdir)).is_file():
            return dbc.Alert("Please, create results (Processing).", color="warning")
        if func is not None:
            return func()
        else:
            raise PreventUpdate

    @app.callback(
        Output("tmpdir", "children"),
        Output("logout-button", "style"),
        Input("progress-interval", "n_intervals"),
    )
    def upate_tmpdir(x):
        if hasattr(app.server, "login_manager"):
            username = current_user.username
            tmpdir = str(TMPDIR / "User" / username)
            return tmpdir, {"visibility": "visible"}
        return str(TMPDIR / "Local"), {"visibility": "hidden"}
    logging.info("Done registering callbacks")


def create_app(**kwargs):
    logging.info('Create application')
    logging.info(f'ms-mint: {ms_mint.__version__}, ({ms_mint.__file__})')
    logging.info(f'ms-mint-app: {ms_mint_app.__version__}, ({ms_mint.__file__})')

    app = dash.Dash(
        __name__,
        long_callback_manager=long_callback_manager,
        external_stylesheets=[
            dbc.themes.MINTY,
            "https://codepen.io/chriddyp/pen/bWLwgP.css",
        ],
        **kwargs,
    )

    app.layout = _layout
    app.title = "MINT"
    app.config["suppress_callback_exceptions"] = True

    upload_root = os.getenv("MINT_DATA_DIR", tempfile.gettempdir())
    CACHE_DIR = str(P(upload_root) / "MINT-Cache")

    logging.info('Defining filesystem cache')
    cache = Cache(
        app.server, config={"CACHE_TYPE": "filesystem", "CACHE_DIR": CACHE_DIR}
    )

    fsc = FileSystemCache(str(CACHEDIR))
    logging.info('Done creating app')
    return app, cache, fsc

