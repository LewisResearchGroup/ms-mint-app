#!/usr/bin/env python

import os
import sys
import subprocess
import multiprocessing
import argparse
import pkg_resources
import xlsxwriter
import bs4
import logging

from waitress import serve
from os.path import expanduser
from pathlib import Path as P
from collections import namedtuple
from multiprocessing import freeze_support

import ms_mint_app


welcome = r"""
 __________________________________________________________________________________________________________
/___/\\\\____________/\\\\__/\\\\\\\\\\\__/\\\\\_____/\\\__/\\\\\\\\\\\\\\\_______________/\\\_____________\
|___\/\\\\\\________/\\\\\\_\/////\\\///__\/\\\\\\___\/\\\_\///////\\\/////______________/\\\\\\\__________|
|____\/\\\//\\\____/\\\//\\\_____\/\\\_____\/\\\/\\\__\/\\\_______\/\\\__________________/\\\\\\\\\________|
|_____\/\\\\///\\\/\\\/_\/\\\_____\/\\\_____\/\\\//\\\_\/\\\_______\/\\\_________________\//\\\\\\\________|
|______\/\\\__\///\\\/___\/\\\_____\/\\\_____\/\\\\//\\\\/\\\_______\/\\\__________________\//\\\\\________|
|_______\/\\\____\///_____\/\\\_____\/\\\_____\/\\\_\//\\\/\\\_______\/\\\___________________\//\\\________|
|________\/\\\_____________\/\\\_____\/\\\_____\/\\\__\//\\\\\\_______\/\\\____________________\///________|
|_________\/\\\_____________\/\\\__/\\\\\\\\\\\_\/\\\___\//\\\\\_______\/\\\_____________________/\\\______|
|__________\///______________\///__\///////////__\///_____\/////________\///_____________________\///______|
\__________________________________________________________________________________________________________/
       \
        \   ^__^
         \  (@@)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
"""


def _create_get_distribution(is_frozen, true_get_distribution, _Dist):
    def _get_distribution(dist):
        if is_frozen and dist == "flask-compress":
            return _Dist("1.5.0")
        else:
            return true_get_distribution(dist)
    return _get_distribution


def main():
    freeze_support()

    HOME = expanduser("~")
    DATADIR = str(P(HOME) / "MINT")
    
    # Define local variables
    is_frozen = hasattr(sys, "_MEIPASS")
    true_get_distribution = pkg_resources.get_distribution
    _Dist = namedtuple("_Dist", ["version"])
    
    # Create the distribution getter function with the necessary context
    get_distribution = _create_get_distribution(is_frozen, true_get_distribution, _Dist)
    
    # Monkey patch the function so it can work once frozen and pkg_resources is of
    # no help
    pkg_resources.get_distribution = get_distribution

    parser = argparse.ArgumentParser(description="MINT frontend.")

    parser.add_argument(
        "--no-browser",
        action="store_true",
        default=False,
        help="do not start the browser",
    )
    parser.add_argument(
        "--version", default=False, action="store_true", help="print current version"
    )
    parser.add_argument(
        "--data-dir", default=DATADIR, help="target directory for MINT data"
    )
    parser.add_argument(
        "--debug",
        default=False,
        action="store_true",
        help="start MINT server in debug mode",
    )
    parser.add_argument("--port", type=int, default=9999, help="Port to use")
    parser.add_argument(
        "--host", type=str, default="127.0.0.1", help="Host binding address"
    )
    parser.add_argument(
        "--serve-path",
        default=None,
        type=str,
        help="(deprecated) serve app at a different path e.g. '/mint/' to serve the app at 'localhost:9999/mint/'",
    )
    parser.add_argument(
        "--ncpu",
        default=None,
        type=int,
        help='Number of CPUs to use',
    )
    args = parser.parse_args()

    if args.version:
        print("Mint version:", ms_mint_app.__version__)
        exit()

    url = f"http://{args.host}:{args.port}"

    # Windows multiprocessing support
    if os.name == "nt":
        # https://github.com/pyinstaller/pyinstaller/wiki/Recipe-Multiprocessing
        multiprocessing.freeze_support()

    if args.data_dir is not None:
        os.environ["MINT_DATA_DIR"] = args.data_dir

    if args.serve_path is not None:
        os.environ["MINT_SERVE_PATH"] = args.serve_path

    print(welcome)

    # Set logging level - use WARNING unless debug mode
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if args.debug else logging.WARNING)

    print("Loading app...")

    from ms_mint_app.app import create_app, register_callbacks

    app, cache, fsc = create_app()
    register_callbacks(app, cache, fsc)

    app.css.config.serve_locally = True
    app.scripts.config.serve_locally = True

    print("Server ready! Opening browser...")

    # Open browser after app is configured and ready
    if not args.no_browser:
        if sys.platform in ["win32", "nt"]:
            os.startfile(url)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", url])
        else:
            try:
                subprocess.Popen(["xdg-open", url])
            except OSError:
                print("Please open a browser on: ", url)
    else:
        print(f"Server starting at {url}")

    if args.debug:
        app.run(
            debug=args.debug,
            port=args.port,
            host=args.host,
            dev_tools_hot_reload=False,
            dev_tools_hot_reload_interval=3000,
            dev_tools_hot_reload_max_retry=30,
        )
    else:
        serve(app.server, port=args.port, host=args.host)


if __name__ == "__main__":
    main()
