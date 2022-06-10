from setuptools import setup, find_packages

import versioneer


with open("README.md", "r") as fh:
    long_description = fh.read()


install_requires = [
    "ms-mint==0.1.7",
    "xlsxwriter",
    "waitress",
    "dash",
    "dash_extensions",
    "dash_bootstrap_components",
    "flask_login",
    "urllib3",
    "dash_tabulator",
    "dash_uploader==0.7.0a1",
]


config = {
    "name": "ms-mint-app",
    "version": versioneer.get_version(),
    "cmdclass": versioneer.get_cmdclass(),
    "description": "Metabolomics Integrator (Mint)",
    "long_description": long_description,
    "long_description_content_type": "text/markdown",
    "author": "Soren Wacker",
    "url": "https://github.com/LewisResearchGroup/ms-mint-app",
    "author_email": "swacker@ucalgary.ca",
    "scripts": ["scripts/Mint.py"],
    "packages": find_packages(),
    "data_files": [("scripts", ["scripts/Mint.py"])],
    "classifiers": [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    "python_requires": ">=3.8",
    "install_requires": install_requires,
    "include_package_data": True,
    "package_data": {
        "ms_mint_app.static": [
            "Standard_Peaklist.csv",
            "ChEBI-Chem.parquet",
            "ChEBI-Groups.parquet",
        ]
    },
}

setup(**config)
