# Contributing to MINT

Thank you for your interest in contributing to the Metabolomics Integrator (MINT)! We welcome all contributions, including bug reports, code reviews, bug fixes, documentation improvements, enhancements, and ideas.

## Getting Started

### Development Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/LewisResearchGroup/ms-mint-app.git
   cd ms-mint-app
   ```

2. **Create a conda environment:**
   ```bash
   conda create -n ms-mint python=3.9
   conda activate ms-mint
   ```

3. **Install the package in development mode:**
   ```bash
   pip install -e .
   ```

4. **Install development dependencies:**
   ```bash
   pip install black flake8
   ```

### Running MINT in Development Mode

Start the application with:
```bash
Mint --debug
```

The `--debug` flag enables debug mode with auto-reloading when files change.

## Code Standards

This project follows [PEP 8](https://www.python.org/dev/peps/pep-0008/) coding standards and uses:

- **Black** for code formatting
- **Flake8** for linting

Before submitting a pull request, please ensure your code is formatted:

```bash
black src/
flake8 src/
```

## Making Changes

### Workflow

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the code standards.

3. Test your changes by running the application:
   ```bash
   Mint --debug
   ```

4. Commit your changes with clear, descriptive commit messages:
   ```bash
   git commit -m "Add feature: description of your changes"
   ```

5. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

6. Open a pull request on GitHub.

### Pull Request Guidelines

- Provide a clear description of the problem and solution
- Reference any related issues
- Include screenshots for UI changes
- Ensure code follows PEP 8 standards
- Update documentation if needed

## Plugin Development

MINT supports a plugin architecture. To develop a plugin:

1. Check out the [plugin template repository](https://github.com/sorenwacker/ms-mint-plugin-template)
2. Plugins should implement the `PluginInterface` defined in `src/ms_mint_app/plugin_interface.py`
3. Place your plugin in the `src/ms_mint_app/plugins/` directory

## Documentation

Documentation is built with [MkDocs](https://www.mkdocs.org/) and hosted on GitHub Pages.

To build documentation locally:
```bash
pip install mkdocs
mkdocs serve
```

Documentation source files are in the `docs/` directory.

## Reporting Issues

When reporting issues, please include:

- MINT version (`Mint --version`)
- Operating system and version
- Python version
- Steps to reproduce the issue
- Expected vs actual behavior
- Screenshots if applicable

## Questions?

If you have questions about contributing, please open a [GitHub issue](https://github.com/LewisResearchGroup/ms-mint-app/issues).

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful and considerate in all interactions.

## License

By contributing to MINT, you agree that your contributions will be licensed under the [Apache License 2.0](LICENSE).
