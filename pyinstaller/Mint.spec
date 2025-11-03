# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_submodules

src_dir = os.path.abspath(os.path.join(SPECPATH, os.pardir))
hooks_dir = os.path.join(src_dir, 'pyinstaller', 'hooks')
script = os.path.join(src_dir, 'src', 'ms_mint_app', 'scripts', 'Mint.py')


# Only collect submodules for packages that PyInstaller typically misses
# For large packages like sklearn, scipy, pyarrow - let PyInstaller's
# automatic detection handle them. This is much faster.
all_hidden_imports = (
    collect_submodules('ms_mint_app')  # Our own package - always include
    + [
        # Add specific hidden imports only if needed
        'bs4',
        'bs4.builder._htmlparser',
        'packaging',
        'packaging.version',
        'packaging.specifiers',
        'packaging.requirements',
        'brotli',
    ]
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
