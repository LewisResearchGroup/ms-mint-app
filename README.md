[![Python package](https://github.com/LewisResearchGroup/ms-mint-app/actions/workflows/pythonpackage.yml/badge.svg)](https://github.com/LewisResearchGroup/ms-mint-app/actions/workflows/pythonpackage.yml)
[![CodeQL](https://github.com/LewisResearchGroup/ms-mint-app/actions/workflows/codeql.yml/badge.svg)](https://github.com/LewisResearchGroup/ms-mint-app/actions/workflows/codeql.yml)
[![Docker Image CI](https://github.com/LewisResearchGroup/ms-mint-app/actions/workflows/docker-image.yml/badge.svg)](https://github.com/LewisResearchGroup/ms-mint-app/actions/workflows/docker-image.yml)
[![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/5178/badge)](https://bestpractices.coreinfrastructure.org/projects/5178)
![PyPI](https://img.shields.io/pypi/v/ms-mint-app?label=pypi%20package)
![PyPI - Downloads](https://img.shields.io/pypi/dm/ms-mint-app)
[![DOI](https://zenodo.org/badge/491654035.svg)](https://zenodo.org/doi/10.5281/zenodo.13121148)

![](docs/image/MINT-logo.jpg)
 
# MINT (Metabolomics Integrator)

The Metabolomics Integrator (MINT) is a web-based post-processing tool for liquid chromatography-mass spectrometry (LC-MS) based metabolomics. MINT enables researchers to extract, visualize, and analyze targeted metabolomics data with an intuitive browser-based interface.

## Overview

Metabolomics is the comprehensive study of small molecule metabolites in biological samples, such as bacterial cultures or human blood. These metabolites serve as critical biomarkers for:
- Disease diagnostics and treatment development
- Pathogen identification (e.g., methicillin-resistant _Staphylococcus aureus_ [MRSA])
- Drug discovery and pharmacology
- Environmental and agricultural research

MINT streamlines the processing of LC-MS data by providing:
- **Targeted peak extraction** with automated and manual retention time optimization
- **Interactive visualizations** including heatmaps, PCA, and hierarchical clustering
- **Quality control tools** for assessing data integrity
- **Flexible data export** for downstream statistical analysis
- **Plugin architecture** for extending functionality

## Getting Started

- **[Installation Guide](https://lewisresearchgroup.github.io/ms-mint-app/install/)** - Install MINT via pip, conda, Docker, or Windows installer
- **[Quickstart Tutorial](https://lewisresearchgroup.github.io/ms-mint-app/quickstart/)** - Step-by-step guide with demo data
- **[Demo Data](https://drive.google.com/drive/folders/1U4xMy5lfETk93sSVXPI79cCWyIMcAjeZ?usp=drive_link)** - Download test data with sample LC-MS files and target lists
- **[Full Documentation](https://lewisresearchgroup.github.io/ms-mint-app/)** - Comprehensive user guide and reference

![Screenshot](https://lewisresearchgroup.github.io/ms-mint-app/image/hierarchical-clustering.png)

## Key Features

### Data Processing
- Import LC-MS data in mzML and mzXML formats
- Define targeted extraction protocols with customizable m/z and retention time windows
- Automated peak detection and retention time optimization
- Batch processing for large datasets

### Interactive Analysis
- Real-time peak shape visualization and quality assessment
- Principal Component Analysis (PCA) for dimensionality reduction
- Hierarchical clustering with dendrograms
- Customizable heatmaps with correlation analysis
- Statistical visualizations (box plots, violin plots, distributions)

### Quality Control
- Mass accuracy (m/z drift) monitoring
- Peak shape evaluation across samples
- Sample type categorization (biological, QC, standards)
- Batch effect visualization

### Data Management
- Workspace-based project organization
- Comprehensive metadata integration
- Multiple export formats (CSV, Excel)
- Support for large-scale studies

## Publications Using MINT

1. Brown K, Thomson CA, Wacker S, et al. [Microbiota alters the metabolome in an age- and sex-dependent manner in mice.](https://pubmed.ncbi.nlm.nih.gov/36906623/) *Nat Commun.* 2023;14:1348.

2. Ponce LF, Bishop SL, Wacker S, Groves RA, Lewis IA. [SCALiR: A Web Application for Automating Absolute Quantification of Mass Spectrometry-Based Metabolomics Data.](https://pubs.acs.org/doi/10.1021/acs.analchem.3c04988) *Anal Chem.* 2024;96:6566–6574.

## Related Software

MINT is developed by the [Lewis Research Group](https://www.lewisresearchgroup.org/). For other metabolomics and computational biology tools, visit [lewisresearchgroup.org/software](https://www.lewisresearchgroup.org/software).

## Development Environment

This project uses the `ms-mint` conda environment. For development and contributing, please refer to the [Installation Guide](https://lewisresearchgroup.github.io/ms-mint-app/install/) for setting up the conda environment.

## Contributing

We welcome contributions of all kinds! Whether you're reporting bugs, suggesting features, improving documentation, or contributing code, your help makes MINT better for everyone.

- **Report Issues**: [GitHub Issues](https://github.com/LewisResearchGroup/ms-mint-app/issues)
- **Contribution Guidelines**: See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and workflow
- **Code Standards**: This project follows PEP 8 and uses Black and Flake8 for code formatting

## Citation

If you use MINT in your research, please cite:

[![DOI](https://zenodo.org/badge/491654035.svg)](https://zenodo.org/doi/10.5281/zenodo.13121148)

Each release is assigned a DOI for proper citation. Visit the DOI link above for version-specific citations.

## Acknowledgements

MINT is built on the shoulders of the open-source community. We are grateful for:

- The Python scientific computing ecosystem (NumPy, Pandas, SciPy, Scikit-learn)
- [Plotly Dash](https://dash.plotly.com/) for the interactive web framework
- GitHub, Docker Hub, and PyPI for hosting and distribution
- The [Plotly Community](https://community.plotly.com/) and [Stack Overflow](https://stackoverflow.com) for invaluable support

**Special thanks to contributors:**
- [@rokm](https://github.com/rokm) - Refactored PyInstaller spec for Windows packaging
- [@bucknerns](https://github.com/bucknerns) - Versioneer configuration

We also thank all users and early adopters whose feedback and bug reports drive continuous improvement.

## License

MINT is licensed under the [Apache License 2.0](LICENSE).

