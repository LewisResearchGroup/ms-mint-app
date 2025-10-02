
# Installation Guide

MINT can be installed via multiple methods. Choose the one that best fits your environment.

## Windows Installer (Recommended for Windows Users)

A standalone Windows installer is available for Windows 10 and 11.

**Download:** [Latest Windows Installer](https://github.com/LewisResearchGroup/ms-mint-app/releases/latest)

**Installation:**
1. Download and run the installer
2. An icon will be added to your Start Menu
3. Launch MINT from the Start Menu
4. A terminal window will appear (you may see harmless error messages—these can be ignored)
5. Wait for the server to start (10–30 seconds)
6. Your browser will open automatically to [http://localhost:9999](http://localhost:9999)
   - If it doesn't, open the URL manually once the terminal shows `Serving on http://127.0.0.1:9999`

## Installation with pip (Recommended for Python Users)

The easiest way to install MINT is via `pip`. This works on Windows, macOS, and Linux.

**Requirements:**
- Python 3.9 or higher

**Installation:**
```bash
pip install ms-mint-app
```

This installs MINT and all dependencies.

**Launch MINT:**
```bash
Mint
```

**Options:**
- `--data-dir /path/to/data` - Specify custom data directory (default: `~/MINT`)
- `--port 8080` - Change the port (default: 9999)
- `--no-browser` - Don't open browser automatically
- `--debug` - Enable debug mode with auto-reload
- `--help` - Show all options

**Example with custom data directory:**
```bash
Mint --data-dir /data/metabolomics
```

## Docker (For Server Deployments)

MINT is available as a Docker container, ideal for server deployments or reproducible environments.

**Pull the latest image:**
```bash
docker pull msmint/msmint:latest
```

**Run MINT:**
```bash
docker run -p 9999:9999 -v /path/to/data:/data msmint/msmint:latest Mint --data-dir /data --no-browser --host 0.0.0.0
```

**Access MINT:**
Open your browser to [http://localhost:9999](http://localhost:9999)

**What this command does:**
- `-p 9999:9999` - Maps port 9999 from container to host
- `-v /path/to/data:/data` - Mounts your local data directory into the container
- `--no-browser` - Prevents auto-opening browser (useful for remote servers)
- `--host 0.0.0.0` - Allows external connections (important for containers)

## Installation from Source (For Developers)

For development or to use the latest unreleased features, install from source.

**Recommended:** Use [conda](https://docs.anaconda.com/free/miniconda/) or [mamba](https://conda-forge.org/miniforge/) to create a virtual environment.

**Steps:**
```bash
# Create and activate conda environment
conda create -n ms-mint python=3.9 pip
conda activate ms-mint

# Clone the repository
git clone https://github.com/LewisResearchGroup/ms-mint-app
cd ms-mint-app

# Install in development mode (editable)
pip install -e .

# Or install normally
pip install .
```

**Development mode (`-e`)** allows you to edit the source code and see changes without reinstalling.

## Troubleshooting

### Browser doesn't open automatically
- Wait for the terminal to show: `INFO:waitress:Serving on http://127.0.0.1:9999`
- Manually open [http://localhost:9999](http://localhost:9999)

### Port already in use
Change the port with `--port`:
```bash
Mint --port 8080
```

### Permission errors on Windows
Run the installer or terminal as Administrator.

### Python version issues
MINT requires Python 3.9 or higher. Check your version:
```bash
python --version
```

## Next Steps

Once installed, proceed to the [Quickstart Tutorial](quickstart.md) to learn how to use MINT.

## Technical Details

- **Frontend**: Built with [Plotly Dash](https://dash.plotly.com/)
- **Backend**: Python with the [ms-mint](https://github.com/LewisResearchGroup/ms-mint) library
- **Server**: Runs locally using Waitress WSGI server
- **Data Storage**: Files stored in `~/MINT` by default (configurable with `--data-dir`)

The MINT GUI is under active development. For programmatic access, you can import and use functions from the `ms-mint` Python library directly in your own scripts.
