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


def show_splash_screen():
    """Show a simple splash screen on Windows while the app loads."""
    try:
        import tkinter as tk
        from tkinter import ttk

        root = tk.Tk()
        root.title("MINT")
        root.overrideredirect(True)  # Remove window decorations

        # Get screen dimensions to center the window
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Splash screen size
        width = 400
        height = 200
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        root.geometry(f"{width}x{height}+{x}+{y}")
        root.configure(bg='#98D8C8')  # Minty theme color

        # MINT text
        title_label = tk.Label(
            root,
            text="MINT",
            font=("Arial", 32, "bold"),
            bg='#98D8C8',
            fg='#ffffff'
        )
        title_label.pack(pady=30)

        # Loading message
        message_label = tk.Label(
            root,
            text="Loading application...",
            font=("Arial", 12),
            bg='#98D8C8',
            fg='#ffffff'
        )
        message_label.pack(pady=10)

        # Progress bar
        progress = ttk.Progressbar(
            root,
            mode='indeterminate',
            length=300
        )
        progress.pack(pady=20)
        progress.start(10)

        # Update the window to show it
        root.update()

        return root
    except:
        # If splash screen fails, just continue without it
        return None




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

    # Show splash screen on Windows (in GUI mode)
    splash = None
    if os.name == "nt" and not args.no_browser and not args.debug:
        splash = show_splash_screen()

    # Windows multiprocessing support
    if os.name == "nt":
        # https://github.com/pyinstaller/pyinstaller/wiki/Recipe-Multiprocessing
        multiprocessing.freeze_support()

    if args.data_dir is not None:
        os.environ["MINT_DATA_DIR"] = args.data_dir

    if args.serve_path is not None:
        os.environ["MINT_SERVE_PATH"] = args.serve_path

    # Set logging level - use WARNING unless debug mode
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if args.debug else logging.WARNING)

    if not splash:
        print("MINT - Metabolomics Integrator")
        print("Loading application...")

    from ms_mint_app.app import create_app, register_callbacks

    # Update splash screen to keep it responsive
    if splash:
        try:
            splash.update()
        except:
            pass

    app, cache, fsc = create_app()

    # Update splash screen
    if splash:
        try:
            splash.update()
        except:
            pass

    register_callbacks(app, cache, fsc)

    app.css.config.serve_locally = True
    app.scripts.config.serve_locally = True

    # Close splash screen if it was shown
    if splash:
        try:
            splash.destroy()
        except:
            pass

    if not splash:
        print("Server ready! Opening browser...")

    # Open browser after app is configured and ready
    if not args.no_browser:
        if sys.platform in ["win32", "nt"]:
            # Try to open Chrome/Edge in app mode first, fallback to default browser
            browser_paths = [
                # Chrome paths
                (os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"), f"--app={url}"),
                (os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"), f"--app={url}"),
                (os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"), f"--app={url}"),
                # Edge paths (pre-installed on Windows 10+)
                (os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"), f"--app={url}"),
                (os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"), f"--app={url}"),
            ]
            opened = False
            for browser_path, flag in browser_paths:
                if os.path.exists(browser_path):
                    try:
                        subprocess.Popen([browser_path, flag])
                        opened = True
                        break
                    except:
                        pass
            if not opened:
                # Fallback to default browser
                os.startfile(url)
        elif sys.platform == "darwin":
            # Try Chrome app mode on macOS, fallback to default
            chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            if os.path.exists(chrome_path):
                try:
                    subprocess.Popen([chrome_path, f"--app={url}"])
                except:
                    subprocess.Popen(["open", url])
            else:
                subprocess.Popen(["open", url])
        else:
            # Linux: try Chrome app mode, fallback to default
            try:
                subprocess.Popen(["google-chrome", f"--app={url}"])
            except OSError:
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
