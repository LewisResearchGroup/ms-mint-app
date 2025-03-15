   
# Installation notes
## Windows Installer
For Windows 10/11 a build is provided [here](https://github.com/soerendip/ms-mint/releases/latest). 
The installer generates an icon in the windows start menu. There will be a terminal be shown, 
with potentially some errors due to missing files which can be ignored. Give it some time until
the server is running and then navigate to [http://localhost:9999](http://localhost:9999) 
in the browser.

## Installation with `pip`
The latest release of the program can easily be installed 
in a standard Python 3 (>= 3.7) environment using the widely used
package manager `pip`:

    pip install ms-mint-app

Should download and install all necessary dependencies and Mint.
Start the app via:

```
Mint
```

## Docker
MINT is now available on DockerHub in containerized format. A container is a standard unit of software that packages up code and all its dependencies, so the application runs quickly and reliably from one computing environment to another. In contrast to a virtual machine (VM), a Docker container image is a lightweight, standalone, executable package of software that includes everything needed to run an application: code, runtime, system tools, system libraries and settings. This allows to run MINT on any computer that can run Docker.

The following command can be used to pull the latest image from docker hub.

    docker pull msmint/msmint:latest

The image can be started with:

    docker run -p 9999:9999 -v /data/:/data/  msmint/msmint:latest Mint --data-dir /data --no-browser --host 0.0.0.0


Then the tool is available in the browser at http://localhost:9999.

## Installation from source
We recommend using [conda](https://docs.anaconda.com/free/miniconda/) or [mamba](https://conda-forge.org/miniforge/) to create a virtual environment before installing `ms-mint-app`.

```bash
# Create conda environment
mamba create -n ms-mint pip
mamba activate ms-mint

# Get the code
git clone https://github.com/LewisResearchGroup/ms-mint-app
cd ms-mint-app

# Install the package normally
pip install .

# Or, install the package in development mode
pip install -e .
```

## Options
After installation Mint can be started by running `Mint`.

```console
Mint --help
usage: Mint [-h] [--no-browser] [--version] [--data-dir DATA_DIR] [--debug] [--port PORT] [--serve-path SERVE_PATH]

MINT frontend.

optional arguments:
  -h, --help            show this help message and exit
  --no-browser          do not start the browser
  --version             print current version
  --data-dir            target directory for MINT data
  --debug               start MINT server in debug mode
  --port                change the port
  --serve-path          serve app at a different path e.g. '/mint/' to serve the app at 'localhost:9999/mint/'
```

If the browser does not open automatically open it manually and navigate to `http://localhost:9999`. The app's frontend is build using [Plotly-Dash](https://plot.ly/dash/) and runs locally in a browser. Thought, the Python functions provided can be imported and used in any Python project independently. The GUI is under active development and may be optimized in the future.
