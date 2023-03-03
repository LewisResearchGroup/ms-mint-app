from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files("ms_mint_app")
hiddenimports = ["ms_mint_app.static"]
