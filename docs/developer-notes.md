# Developer Notes

## Building and Uploading the Package

To build the source distribution and wheel for `ms-mint-app`, follow these steps:

1. Navigate to the root directory of the project.
2. Ensure you have `build` and `twine` installed:

```bash
pip install build twine
```

3. Build the package using `pyproject.toml`:

```bash
python -m build
```

   This will generate distribution archives in the `dist` directory (both `.tar.gz` and `.whl` files).

4. To upload the built package to PyPI, use `twine`:

```bash
python -m twine upload dist/*
```

   This command will upload all distribution files to PyPI.

## Windows Executables

To create Windows executables for the `ms-mint` application, use `pyinstaller`. Follow these steps:

1. Navigate to the `specfiles` directory.
2. Run the `pyinstaller` command with the provided specification file:

```bash
cd specfiles && pyinstaller --noconfirm Mint.spec ..\scripts\Mint.py
```

   This will generate a standalone executable for Windows based on the `Mint.spec` file.

## Documentation Deployment

To build and deploy the documentation using `mkdocs`, follow these steps:

1. Ensure you have `mkdocs` installed (`pip install mkdocs` if not).
2. Run the following commands to build the documentation and deploy it to GitHub Pages:

```bash
mkdocs build && mkdocs gh-deploy
```

   The `mkdocs build` command generates the static site in the `site` directory, and `mkdocs gh-deploy` pushes it to the `gh-pages` branch of your GitHub repository.

## Example NGINX Configuration

To run `ms-mint` on a remote server, you need to set up a reverse proxy using NGINX. Here is an example configuration:

    server {
        ...
        location / {
            proxy_pass              http://localhost:8000;
            client_max_body_size    100G;
            proxy_set_header        X-Forwarded-Proto https;
            proxy_set_header        Host $host;
        }
    }

Explanation:

  - `proxy_pass http://localhost:8000;`: Forwards all requests to the `ms-mint` application running on port 8000.
  - `client_max_body_size 100G;`: Increases the maximum allowed size of client request bodies to 100GB.
  - `proxy_set_header X-Forwarded-Proto https;`: Sets the `X-Forwarded-Proto` header to `https`.
  - `proxy_set_header Host $host;`: Ensures the `Host` header from the original request is passed to the proxied server.

Then start ms-mint via the `entrypoint.sh` script.