import os
import io
import shutil
import base64
import subprocess
import platform
import logging

import numpy as np
import pandas as pd

from tqdm import tqdm
from glob import glob
from pathlib import Path as P

import urllib3, ftplib
from urllib.parse import urlparse
from bs4 import BeautifulSoup

import matplotlib as mpl

mpl.use("Agg")

from matplotlib import pyplot as plt
import matplotlib.cm as cm

import ms_mint
from ms_mint.io import ms_file_to_df
from ms_mint.targets import standardize_targets, read_targets
from ms_mint.io import convert_ms_file_to_feather
from ms_mint.standards import TARGETS_COLUMNS

from datetime import date

from .filelock import FileLock


def list_to_options(x):
    return [{"label": e, "value": e} for e in x]


def lock(fn):
    return FileLock(f"{fn}.lock", timeout=1)


def today():
    return date.today().strftime("%y%m%d")


def get_versions():
    string = ""
    try:
        string += subprocess.getoutput("conda env export --no-build")
    except:
        pass
    return string


def get_issue_text():
    return f"""
    %0A%0A%0A%0A%0A%0A%0A%0A%0A
    MINT version: {ms_mint.__version__}%0A
    OS: {platform.platform()}%0A
    Versions: ---
    """


def parse_ms_files(contents, filename, date, target_dir):
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    fn_abs = os.path.join(target_dir, filename)
    with lock(fn_abs):
        with open(fn_abs, "wb") as file:
            file.write(decoded)
    new_fn = convert_ms_file_to_feather(fn_abs)
    if os.path.isfile(new_fn):
        os.remove(fn_abs)


def parse_pkl_files(contents, filename, date, target_dir, ms_mode=None):
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
    df = standardize_targets(df, ms_mode=ms_mode)
    df = df.drop_duplicates()
    return df


def get_dirnames(path):
    dirnames = [f.name for f in os.scandir(path) if f.is_dir()]
    return dirnames


def workspace_path(tmpdir, ws_name):
    return os.path.join(tmpdir, "workspaces", ws_name)


def maybe_migrate_workspaces(tmpdir):
    if not P(tmpdir).is_dir():
        return None
    dir_names = get_dirnames(tmpdir)
    ws_path = get_workspaces_path(tmpdir)
    if not os.path.isdir(ws_path) and len(dir_names) > 0:
        logging.info("Migrating to new directory scheme.")
        os.makedirs(ws_path)
        for dir_name in dir_names:
            old_dir = os.path.join(tmpdir, dir_name)
            new_dir = workspace_path(tmpdir, dir_name)
            shutil.move(old_dir, new_dir)
            logging.info("Moving", old_dir, "to", new_dir)


def maybe_update_workpace_scheme(wdir):
    old_pkl_fn = P(wdir) / "peaklist" / "peaklist.csv"
    new_pkl_fn = P(get_targets_fn(wdir))
    new_path = new_pkl_fn.parent
    old_path = old_pkl_fn.parent
    if old_pkl_fn.is_file():
        logging.info(f"Moving targets file to new default location ({new_pkl_fn}).")
        if not new_path.is_dir():
            os.makedirs(new_path)
        os.rename(old_pkl_fn, new_pkl_fn)
        shutil.rmtree(old_path)


def workspace_exists(tmpdir, ws_name):
    path = workspace_path(tmpdir, ws_name)
    return os.path.isdir(path)


def get_active_workspace(tmpdir):
    """Returns name of last activated workspace,
    if workspace still exists. Otherwise,
    return None.
    """
    fn_ws_info = os.path.join(tmpdir, ".active-workspace")
    if not os.path.isfile(fn_ws_info):
        return None
    with open(fn_ws_info, "r") as file:
        ws_name = file.read()
    if ws_name in get_workspaces(tmpdir):
        return ws_name
    else:
        return None


def save_activated_workspace(tmpdir, ws_name):
    fn_ws_info = os.path.join(tmpdir, ".active-workspace")
    with open(fn_ws_info, "w") as file:
        file.write(ws_name)


def create_workspace(tmpdir, ws_name):
    path = workspace_path(tmpdir, ws_name)
    assert not os.path.isdir(path)
    os.makedirs(path)
    os.makedirs(os.path.join(path, "ms_files"))
    os.makedirs(os.path.join(path, "targets"))
    os.makedirs(os.path.join(path, "results"))
    os.makedirs(os.path.join(path, "figures"))
    os.makedirs(os.path.join(path, "chromato"))


def get_workspaces_path(tmpdir):
    # Defines the path to the workspaces
    # relative to `tmpdir`
    return os.path.join(tmpdir, "workspaces")


def get_workspaces(tmpdir):
    ws_path = get_workspaces_path(tmpdir)
    if not P(ws_path).is_dir():
        return []
    ws_names = get_dirnames(ws_path)
    ws_names = [ws for ws in ws_names if not ws.startswith(".")]
    ws_names.sort()
    return ws_names


class Chromatograms:
    def __init__(self, wdir, targets, ms_files, progress_callback=None):
        self.wdir = wdir
        self.targets = targets
        self.ms_files = ms_files
        self.n_peaks = len(targets)
        self.n_files = len(ms_files)
        self.progress_callback = progress_callback

    def create_all(self):
        for fn in tqdm(self.ms_files):
            self.create_all_for_ms_file(fn)
        return self

    def create_all_for_ms_file(self, ms_file: str):
        fn = ms_file
        df = ms_file_to_df(fn)
        for ndx, row in self.targets.iterrows():
            mz_mean, mz_width = row[["mz_mean", "mz_width"]]
            fn_chro = get_chromatogram_fn(fn, mz_mean, mz_width, self.wdir)
            if os.path.isfile(fn_chro):
                continue
            dirname = os.path.dirname(fn_chro)
            if not os.path.isdir(dirname):
                os.makedirs(dirname)
            dmz = mz_mean * 1e-6 * mz_width
            chrom = df[(df["mz"] - mz_mean).abs() <= dmz]
            chrom["scan_time"] = chrom["scan_time"].round(3)
            chrom = chrom.groupby("scan_time").max().reset_index()
            chrom[["scan_time", "intensity"]].to_feather(fn_chro)

    def get_single(self, mz_mean, mz_width, ms_file):
        return get_chromatogram(ms_file, mz_mean, mz_width, self.wdir)


def create_chromatograms(ms_files, targets, wdir):
    for fn in tqdm(ms_files):
        fn_out = os.path.basename(fn)
        fn_out, _ = os.path.splitext(fn_out)
        fn_out += ".feather"
        for ndx, row in targets.iterrows():
            mz_mean, mz_width = row[["mz_mean", "mz_width"]]
            fn_chro = get_chromatogram_fn(fn, mz_mean, mz_width, wdir)
            if not os.path.isfile(fn_chro):
                create_chromatogram(fn, mz_mean, mz_width, fn_chro)


def create_chromatogram(ms_file, mz_mean, mz_width, fn_out):
    df = ms_file_to_df(ms_file)
    dirname = os.path.dirname(fn_out)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
    dmz = mz_mean * 1e-6 * mz_width
    chrom = df[(df["mz"] - mz_mean).abs() <= dmz]
    chrom["scan_time"] = chrom["scan_time"].round(3)
    chrom = chrom.groupby("scan_time").max().reset_index()
    with lock(fn_out):
        chrom[["scan_time", "intensity"]].to_feather(fn_out)
    return chrom


def get_chromatogram(ms_file, mz_mean, mz_width, wdir):
    fn = get_chromatogram_fn(ms_file, mz_mean, mz_width, wdir)
    if not os.path.isfile(fn):
        chrom = create_chromatogram(ms_file, mz_mean, mz_width, fn)
    else:
        try:
            chrom = pd.read_feather(fn)
        except:
            os.remove(fn)
            logging.warning(f"Cound not read {fn}.")
            return None

    chrom = chrom.rename(
        columns={
            "retentionTime": "scan_time",
            "intensity array": "intensity",
            "m/z array": "mz",
        }
    )

    return chrom


def get_chromatogram_fn(ms_file, mz_mean, mz_width, wdir):
    ms_file = os.path.basename(ms_file)
    base, _ = os.path.splitext(ms_file)
    fn = (
        os.path.join(wdir, "chromato", f"{mz_mean}-{mz_width}".replace(".", "_"), base)
        + ".feather"
    )
    return fn


def get_targets_fn(wdir):
    return os.path.join(wdir, "targets", "targets.csv")


def get_targets(wdir):
    fn = get_targets_fn(wdir)
    if os.path.isfile(fn):
        targets = read_targets(fn).set_index("peak_label")
    else:
        targets = pd.DataFrame(columns=TARGETS_COLUMNS)
    return targets


def update_targets(wdir, peak_label, rt_min=None, rt_max=None, rt=None):
    targets = get_targets(wdir)

    if isinstance(peak_label, str):
        if rt_min is not None and not np.isnan(rt_min):
            targets.loc[peak_label, "rt_min"] = rt_min
        if rt_max is not None and not np.isnan(rt_max):
            targets.loc[peak_label, "rt_max"] = rt_max
        if rt is not None and not np.isnan(rt):
            targets.loc[peak_label, "rt"] = rt

    if isinstance(peak_label, int):
        targets = targets.reset_index()
        if rt_min is not None and not np.isnan(rt_min):
            targets.loc[peak_label, "rt_min"] = rt_min
        if rt_max is not None and not np.isnan(rt_max):
            targets.loc[peak_label, "rt_max"] = rt_max
        if rt is not None and not np.isnan(rt):
            targets.loc[peak_label, "rt"] = rt
        targets = targets.set_index("peak_label")

    fn = get_targets_fn(wdir)
    with lock(fn):
        targets.to_csv(fn)


def get_results_fn(wdir):
    return os.path.join(wdir, "results", "results.csv")


def get_results(wdir):
    fn = get_results_fn(wdir)
    df = pd.read_csv(fn)
    df["ms_file_label"] = [filename_to_label(fn) for fn in df["ms_file"]]
    return df


def get_metadata(wdir):
    fn = get_metadata_fn(wdir)
    fn_path = os.path.dirname(fn)
    ms_files = get_ms_fns(wdir, abs_path=False)
    ms_files = [filename_to_label(fn) for fn in ms_files]
    df = None
    if not os.path.isdir(fn_path):
        os.makedirs(fn_path)
    if os.path.isfile(fn):
        df = pd.read_csv(fn)
        if "ms_file_label" not in df.columns:
            df = None

    if df is None or len(df) == 0:
        df = init_metadata(ms_files)

    for col in [
        "color",
        "plate_column",
        "plate_row",
        "plate",
        "label",
        "in_analysis",
        "use_for_optimization",
        "ms_file_label",
        "ms_column",
        "ionization_mode",
    ]:
        if col not in df.columns:
            df[col] = None

    df = df[df["ms_file_label"] != ""]

    new_files = [e for e in ms_files if e not in df['ms_file_label'].values]

    df = df.groupby("ms_file_label").first().reindex(ms_files, ).reset_index()
    
    if new_files :
        # Default for use_for_optimization for new files should be False
        ndx = df[df['ms_file_label'].isin(new_files)].index
        df.loc[ndx, 'use_for_optimization'] = False

    if "use_for_optimization" not in df.columns:
        df["use_for_optimization"] = False

    else:
        df["use_for_optimization"] = df["use_for_optimization"].astype(bool)

    if "in_analysis" not in df.columns:
        df["in_analysis"] = True
    else:
        df["in_analysis"] = df["in_analysis"].astype(bool)

    if "index" in df.columns:
        del df["index"]

    df["plate_column"] = df["plate_column"].apply(format_columns)

    df["sample_type"] = df["sample_type"].fillna("Not set")

    df.reset_index(inplace=True)

    return df


def init_metadata(ms_files):
    ms_files = list(ms_files)
    ms_files = [filename_to_label(fn) for fn in ms_files]
    df = pd.DataFrame({"ms_file_label": ms_files})
    df["in_analysis"] = True
    df["label"] = ""
    df["color"] = None
    df["sample_type"] = "Unknown"
    df["run_order"] = ""
    df["plate"] = ""
    df["plate_row"] = ""
    df["plate_column"] = ""
    df["use_for_optimization"] = ""
    return df


def write_metadata(meta, wdir):
    fn = get_metadata_fn(wdir)
    with lock(fn):
        meta.to_csv(fn, index=False)


def get_metadata_fn(wdir):
    fn = os.path.join(wdir, "metadata", "metadata.csv")
    return fn


def get_ms_dirname(wdir):
    return os.path.join(wdir, "ms_files")


def get_ms_fns(wdir, abs_path=True):
    path = get_ms_dirname(wdir)
    fns = glob(os.path.join(path, "**", "*.*"), recursive=True)
    fns = [fn for fn in fns if is_ms_file(fn)]
    if not abs_path:
        fns = [os.path.basename(fn) for fn in fns]
    return fns


def is_ms_file(fn: str):
    if (
        fn.lower().endswith(".mzxml")
        or fn.lower().endswith(".mzml")
        or fn.lower().endswith(".feather")
    ):
        return True
    return False


def Basename(fn):
    fn = os.path.basename(fn)
    fn, _ = os.path.splitext(fn)
    return fn


def format_columns(x):
    try:
        if isinstance(x, str):
            if x in ["", "null", "None"]:
                return None
            else:
                return x
        elif x is None:
            return None
        elif np.isnan(x):
            return None
    except:
        assert False
    return f"{int(x):02.0f}"


def get_complete_results(
    wdir,
    include_labels=None,
    exclude_labels=None,
    file_types=None,
    include_excluded=False,
):
    meta = get_metadata(wdir)
    resu = get_results(wdir)

    if not include_excluded:
        meta = meta[meta["in_analysis"]]
    df = pd.merge(meta, resu, on=["ms_file_label"])
    if include_labels is not None and len(include_labels) > 0:
        df = df[df.peak_label.isin(include_labels)]
    if exclude_labels is not None and len(exclude_labels) > 0:
        df = df[~df.peak_label.isin(exclude_labels)]
    if file_types is not None and file_types != []:
        df = df[df.sample_type.isin(file_types)]
    df["log(peak_max+1)"] = df.peak_max.apply(np.log1p)
    if "index" in df.columns:
        df = df.drop("index", axis=1)
    return df


def gen_tabulator_columns(
    col_names=None,
    add_ms_file_col=False,
    add_color_col=False,
    add_peakopt_col=False,
    add_ms_file_active_col=False,
    col_width="12px",
    editor="input",
):

    if col_names is None:
        col_names = []
    col_names = list(col_names)

    standard_columns = [
        "ms_file_label",
        "in_analysis",
        "color",
        "index",
        "use_for_optimization",
    ]

    for col in standard_columns:
        if col in col_names:
            col_names.remove(col)

    columns = [
        {
            "formatter": "rowSelection",
            "titleFormatter": "rowSelection",
            "titleFormatterParams": {
                "rowRange": "active"  # only toggle the values of the active filtered rows
            },
            "hozAlign": "center",
            "headerSort": False,
            "width": "1px",
            "frozen": True,
        }
    ]

    if add_ms_file_col:
        columns.append(
            {
                "title": "ms_file_label",
                "field": "ms_file_label",
                "headerFilter": True,
                "headerSort": True,
                "editor": "input",
                "sorter": "string",
                "frozen": True,
            }
        )

    if add_color_col:
        columns.append(
            {
                "title": "color",
                "field": "color",
                "headerFilter": False,
                "editor": "input",
                "formatter": "color",
                "width": "3px",
                "headerSort": False,
            }
        )

    if add_peakopt_col:
        columns.append(
            {
                "title": "use_for_optimization",
                "field": "use_for_optimization",
                "headerFilter": False,
                "formatter": "tickCross",
                "width": "6px",
                "headerSort": True,
                "hozAlign": "center",
                "editor": True,
            }
        )

    if add_ms_file_active_col:
        columns.append(
            {
                "title": "in_analysis",
                "field": "in_analysis",
                "headerFilter": True,
                "formatter": "tickCross",
                "width": "6px",
                "headerSort": True,
                "hozAlign": "center",
                "editor": True,
            }
        )

    for col in col_names:
        content = {
            "title": col,
            "field": col,
            "headerFilter": True,
            "width": col_width,
            "editor": editor,
        }

        columns.append(content)
    return columns


def parse_table_content(content, filename):
    content_type, content_string = content.split(",")
    decoded = base64.b64decode(content_string)
    if filename.lower().endswith(".csv"):
        df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
    elif filename.lower().endswith(".xlsx"):
        df = pd.read_excel(io.BytesIO(decoded))
    return df


def fig_to_src(fig, dpi=100):
    out_img = io.BytesIO()
    fig.savefig(out_img, format="jpeg", bbox_inches="tight", dpi=dpi)
    plt.close(fig)
    out_img.seek(0)  # rewind file
    encoded = base64.b64encode(out_img.read()).decode("ascii").replace("\n", "")
    return "data:image/png;base64,{}".format(encoded)


def merge_metadata(old: pd.DataFrame, new: pd.DataFrame, index_col='ms_file_label') -> pd.DataFrame:
    """
    This function updates one existing dataframe 
    with information from a second dataframe.
    If a column of the new dataframe does not 
    exist it will be created.

    Parameters:
    old (pd.DataFrame): The DataFrame to merge new data into.
    new (pd.DataFrame): The DataFrame containing the new data to merge.

    Returns:
    pd.DataFrame: The merged DataFrame.

    """    
    old = old.set_index(index_col)

    new = new.groupby(index_col).first().replace("null", None)

    for col in new.columns:
        if col == "" or col.startswith("Unnamed"):
            continue
        if not col in old.columns:
            old[col] = None
        for ndx in new.index:
            value = new.loc[ndx, col]
            if value is None:
                continue
            if ndx in old.index:
                old.loc[ndx, col] = value

    return old.reset_index()


def file_colors(wdir):
    meta = get_metadata(wdir)
    colors = {}
    for ndx, (fn, co) in meta[["ms_file_label", "color"]].iterrows():
        if not (isinstance(co, str)):
            co = None
        colors[fn] = co
    return colors


def get_figure_fn(kind, wdir, label, format):
    path = os.path.join(wdir, "figures", kind)
    clean_label = clean_string(label)
    fn = f"{kind}__{clean_label}.{format}"
    fn = os.path.join(path, fn)
    return path, fn


def clean_string(fn: str):
    for x in ['"', "'", "(", ")", "[", "]", " ", "\\", "/", "{", "}"]:
        fn = fn.replace(x, "_")
    return fn


def savefig(fig, kind=None, wdir=None, label=None, format="png", dpi=150):
    path, fn = get_figure_fn(kind=kind, wdir=wdir, label=label, format=format)
    maybe_create(path)
    try:
        with lock(fn):
            fig.savefig(fn, dpi=dpi, bbox_inches="tight")
    except:
        logging.error(f"Could not save figure {fn}, maybe no figure was created: {label}")
    return fn


def maybe_create(dir_name):
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)


def png_fn_to_src(fn):
    encoded_image = base64.b64encode(open(fn, "rb").read())
    return "data:image/png;base64,{}".format(encoded_image.decode())


def get_ms_fns_for_peakopt(wdir):
    """Extract the filenames for peak optimization from
    the metadata table and recreate the complete filename."""
    df = get_metadata(wdir)
    fns = df[df.use_for_optimization.astype(bool) == True]["ms_file_label"]
    ms_files = get_ms_fns(wdir)
    mapping = {filename_to_label(fn): fn for fn in ms_files}
    fns = [mapping[fn] for fn in fns]
    return fns


def float_to_color(x, vmin=0, vmax=2, cmap=None):
    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    m = cm.ScalarMappable(norm=norm, cmap=cmap)
    return m.to_rgba(x)


def write_targets(targets, wdir):
    fn = get_targets_fn(wdir)
    if "peak_label" in targets.columns:
        targets = targets.set_index("peak_label")
    with lock(fn):
        targets.to_csv(fn)


def filename_to_label(fn: str):
    if is_ms_file(fn):
        fn = os.path.splitext(fn)[0]
    return os.path.basename(fn)


def get_filenames_from_url(url):
    if url.startswith("ftp"):
        return get_filenames_from_ftp_directory(url)
    if "://" in url:
        url = url.split("://")[1]
    with urllib3.PoolManager() as http:
        r = http.request("GET", url)
    soup = BeautifulSoup(r.data, "html")
    files = [A["href"] for A in soup.find_all("a", href=True)]
    return files


def get_filenames_from_ftp_directory(url):
    url_parts = urlparse(url)
    domain = url_parts.netloc
    path = url_parts.path
    ftp = ftplib.FTP(domain)
    ftp.login()
    ftp.cwd(path)
    filenames = ftp.nlst()
    ftp.quit()
    return filenames


def import_from_local_path(path, target_dir, fsc=None):
    fns = glob(os.path.join(path, "**", "*.*"), recursive=True)
    fns = [fn for fn in fns if is_ms_file(fn)]
    fns_out = []
    n_files = len(fns)
    for i, fn in enumerate(tqdm(fns)):
        if fsc is not None:
            fsc.set("progress", int(100 * (1 + i) / n_files))
        fn_out = P(target_dir) / P(fn).with_suffix(".feather").name
        if P(fn_out).is_file():
            continue
        fns_out.append(fn_out)
        try:
            convert_ms_file_to_feather(fn, fn_out)
        except:
            logging.warning(f"Could not convert {fn}")
    return fns_out


def df_to_in_memory_csv_file(df):
    buffer = io.StringIO()
    df.to_csv(buffer)
    buffer.seek(0)
    return buffer.getvalue


def df_to_in_memory_excel_file(df):
    def to_xlsx(bytes_io):
        xslx_writer = pd.ExcelWriter(bytes_io, engine="xlsxwriter")
        df.to_excel(xslx_writer, index=True, sheet_name="sheet1")
        xslx_writer.close()

    return to_xlsx


def has_na(df):
    return df.isna().sum().sum() > 0


def fix_first_emtpy_line_after_upload_workaround(file_path):
    logging.warning(f'Check if first line is empty in {file_path}.')

    with open(file_path, 'r') as file:
        lines = file.readlines()

    if not lines:
        return

    # Check if the first line is an empty line (contains only newline character)
    if lines[0] == "\n":
        logging.warning(f'Empty first line detected in {file_path}. Removing it.')
        lines.pop(0)
        
        with open(file_path, 'w') as file:
            file.writelines(lines)


def describe_transformation(var_name, apply, groupby, scaler):

    # Only apply the function if it's provided
    if apply is not None:
        apply_desc = transformations[apply]['description']
        apply_desc = apply_desc.replace('x', var_name)
    else:
        apply_desc = var_name
    
    # If scaler or groupby is None, no scaling applied so return just the transformed variable
    if groupby is None or scaler is None:
        return apply_desc

    if not scaler:
        return apply_desc

    # Define human-readable names for known scalers
    scaler_mapping = {"standard": "Standard scaling", "robust": "Robust scaling", '': ''}  # expand as needed
    if isinstance(scaler, str):
        scaler_description = scaler_mapping.get(scaler.lower(), scaler)
    else:
        scaler_description = scaler.__name__
    
    # Groupby can be a list or a string, so make sure it's a list for consistent handling
    if isinstance(groupby, str):
        groupby = [groupby]
    
    groupby_description = ", ".join(groupby)
    
    # Scaling was applied, so return the description in < >
    return f"<{apply_desc}> ({scaler_description}, grouped by {groupby_description})"


log2p1 = lambda x: np.log2(1 + x)
log1p = np.log1p

transformations = {
    "log1p":  {'function': log1p,  'description': 'log10(x + 1)'},
    "log2p1": {'function': log2p1, 'description': 'log2(x + 1)' }
}