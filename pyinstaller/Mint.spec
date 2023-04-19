# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_submodules

src_dir = os.path.abspath(os.path.join(SPECPATH, os.pardir))
hooks_dir = os.path.join(src_dir, 'pyinstaller', 'hooks')
script = os.path.join(src_dir, 'scripts', 'Mint.py')


all_hidden_imports = (
    collect_submodules('sklearn')
    + collect_submodules('bs4')
    + collect_submodules('scipy')
    + collect_submodules('pyarrow')
    + collect_submodules('ms_mint_app')
    + collect_submodules('packaging')
    + collect_submodules('brotli')
)


a = Analysis(
    [script],
    pathex=[src_dir],
    hookspath=[hooks_dir],
    hiddenimports=all_hidden_imports,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name='Mint',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='Mint',
)
