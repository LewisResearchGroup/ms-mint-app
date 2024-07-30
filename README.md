[![Python package](https://github.com/LewisResearchGroup/ms-mint-app/actions/workflows/pythonpackage.yml/badge.svg)](https://github.com/LewisResearchGroup/ms-mint-app/actions/workflows/pythonpackage.yml)
[![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/5178/badge)](https://bestpractices.coreinfrastructure.org/projects/5178)
![](images/coverage.svg)
[![Docker Image CI](https://github.com/LewisResearchGroup/ms-mint-app/actions/workflows/docker-image.yml/badge.svg)](https://github.com/LewisResearchGroup/ms-mint-app/actions/workflows/docker-image.yml)
![PyPI](https://img.shields.io/pypi/v/ms-mint-app?label=pypi%20package)
![PyPI - Downloads](https://img.shields.io/pypi/dm/ms-mint-app)
[![DOI](https://zenodo.org/badge/491654035.svg)](https://zenodo.org/doi/10.5281/zenodo.13121148)

![](docs/image/MINT-logo.jpg)

# MINT (Metabolomics Integrator)
The Metabolomics Integrator (MINT) is a post-processing tool for liquid chromatography-mass spectrometry (LCMS) based metabolomics. 
Metabolomics is the study of all metabolites (small chemical compounds) in a biological sample e.g. from bacteria or a human blood sample. 
The metabolites can be used to define biomarkers used in medicine to find treatments for diseases or for the development of diagnostic tests 
or for the identification of pathogens such as methicillin resistant _Staphylococcus aureus_ (MRSA). 
More information on how to install and run the program can be found in the [Documentation](https://LewisResearchGroup.github.io/ms-mint-app/) or check out the 
[Tutorial](https:///LewisResearchGroup.github.io/ms-mint-app/quickstart/) to jump right into it.

![Screenshot](docs/gallery/MINT-interface-1.png)

## News
Starting with version 1.0.0, we have updated the installation setup to use pyproject.toml. Additionally, the main script to start Mint has been changed from Mint.py to Mint. Furthermore, each release of the repository will now be assigned a DOI to facilitate citation of the software.

## Publications that used Mint
1. Brown K, Thomson CA, Wacker S, Drikic M, Groves R, Fan V, et al. [Microbiota alters the metabolome in an age- and sex- dependent manner in mice.](https://pubmed.ncbi.nlm.nih.gov/36906623/) Nat Commun. 2023;14: 1348.

2. Ponce LF, Bishop SL, Wacker S, Groves RA, Lewis IA. [SCALiR: A Web Application for Automating Absolute Quantification of Mass Spectrometry-Based Metabolomics Data. Anal Chem.](https://pubs.acs.org/doi/10.1021/acs.analchem.3c04988) 2024;96: 6566–6574.

## Installation
You can find installation instructions [here](https://lewisresearchgroup.github.io/ms-mint-app/install/)

## Contributions
All contributions, bug reports, code reviews, bug fixes, documentation improvements, enhancements, and ideas are welcome. This includes recommendations for software architecture, code design, and efficiency improvements. 

## Code standards
The project follows PEP8 standard and uses Black and Flake8 to ensure a consistent code format throughout the project.

## Get in touch
To get in touch, please open a GitHub [issue](https://github.com/LewisResearchGroup/ms-mint-app/issues).

## Acknowledgements
This project would not be possible without the help of the open-source community. 
The tools and resources provided by GitHub, Docker-Hub, the Python Package Index, as well the answers from dedicated users on [Stackoverflow](stackoverflow.com)
and the [Plotly community](https://community.plotly.com/), as well as the free open-source packages used are the foundation of this project.
Several people have made direct contributions to the codebase and we are extremely grateful for that. 

- @rokm refactored the specfile for `Pyinstaller` to create a windows package. 
- @bucknerns helped with the configuration of the `versioneer` file.

Last but not least, we want to thank all the users and early adopters that drive the development with feature requests and bug reports.

