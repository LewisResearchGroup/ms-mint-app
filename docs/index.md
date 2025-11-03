# MINT - Metabolomics Integrator

MINT is a comprehensive toolkit for **liquid chromatography-mass spectrometry (LC-MS)** based metabolomics, providing both a powerful Python library and an intuitive web-based interface for extracting, visualizing, and analyzing targeted metabolomics data from complex biological samples.

![Screenshot](quickstart/peak-preview.png)
_**Figure 1:** MINT browser interface showing interactive peak preview with retention time optimization._

## Why MINT?

Metabolomics—the comprehensive study of small molecule metabolites in biological samples—plays a critical role in:

- **Biomedical Research**: Identifying biomarkers for disease diagnostics and therapeutic development
- **Pathogen Detection**: Distinguishing bacterial strains (e.g., methicillin-resistant _Staphylococcus aureus_ [MRSA])
- **Drug Discovery**: Understanding metabolic pathways and drug effects
- **Environmental Science**: Tracking metabolic responses to environmental changes

MINT streamlines the LC-MS data processing workflow with powerful features for targeted metabolite quantification, quality assessment, and statistical analysis. It is particularly well-suited for handling **large amounts of data (10,000+ files)**.

## Quick Links

- **[Quickstart Tutorial](quickstart.md)** - Get started with demo data in minutes
- **[Installation Guide](install.md)** - Multiple installation options (pip, conda, Docker, Windows)
- **[Demo Data](https://drive.google.com/drive/folders/1U4xMy5lfETk93sSVXPI79cCWyIMcAjeZ?usp=drive_link)** - Download test data with sample LC-MS files and target lists
- **[GUI Documentation](gui.md)** - Detailed interface guide
- **[Target Lists](targets.md)** - How to define extraction protocols
- **[Python Library Documentation](https://lewisresearchgroup.github.io/ms-mint)** - Core ms-mint library for scripts and notebooks

## Resources

- **[Lewis Research Group Software](https://www.lewisresearchgroup.org/software)** - Explore additional metabolomics and computational biology tools
- [GitHub: ms-mint-app](https://github.com/LewisResearchGroup/ms-mint-app) - Web application (this project)
- [GitHub: ms-mint](https://github.com/LewisResearchGroup/ms-mint) - Core Python library
- [Plugin Template](https://github.com/sorenwacker/ms-mint-plugin-template) - Extend MINT functionality

## Understanding LC-MS Metabolomics

### The Challenge

Biological samples (e.g., blood, tissue, bacterial cultures) contain thousands of [metabolites](https://en.wikipedia.org/wiki/Metabolite)—sugars, amino acids, nucleotides, lipids, and more. [Mass spectrometry](https://en.wikipedia.org/wiki/Mass_spectrometry) can measure these compounds with high sensitivity and accuracy, but many metabolites share identical or very similar masses, making them indistinguishable by mass alone.

### The Solution: Liquid Chromatography

To separate metabolites before mass spectrometry analysis, [liquid chromatography (LC)](https://en.wikipedia.org/wiki/Liquid_chromatography) is used. As the sample flows through a chromatographic column, metabolites interact differently with the column material based on their chemical properties. This causes metabolites to **elute** (exit the column) at different **retention times**, spreading them out over time so they can be measured individually by the mass spectrometer.

### LC-MS Data Structure

The mass spectrometer continuously measures ion intensities across a range of mass-to-charge (m/z) values as metabolites elute from the column. This produces a three-dimensional dataset: **retention time**, **m/z**, and **intensity**.

![](image/demo_Saureus_sample_raw.png)<br/>
_**Figure 2:** 2D heatmap of LC-MS data from _S. aureus_ showing ion intensities over 10 minutes for m/z 100–600. Brighter colors indicate higher ion abundance._

Zooming into a narrow m/z range reveals individual metabolite peaks. For example, here is the extracted ion chromatogram for succinate ([succinic acid](https://en.wikipedia.org/wiki/Succinic_acid)):

![](image/demo_Saureus_sample_raw_succinate.png)<br/>
_**Figure 3:** Zoomed view showing the chromatographic peak for succinate. The sharp peak indicates high signal and good chromatographic separation._

This demonstrates the precision of LC-MS data—mass measurements are accurate to fractions of a Dalton (for comparison, an electron has m/z = 5.489×10⁻⁴).

## How MINT Processes LC-MS Data

### Data Conversion

Raw LC-MS data is typically stored in vendor-specific formats (e.g., Thermo .raw, Agilent .d). MINT requires data to be converted to open formats:
- **mzML** (preferred)
- **mzXML**

Most vendor software provides conversion tools, or you can use open-source converters like [MSConvert](http://proteowizard.sourceforge.net/tools.shtml).

### Targeted Peak Extraction

Rather than analyzing the entire LC-MS dataset, MINT uses a **targeted approach**:

1. **Define targets**: Specify metabolites by their expected m/z and retention time (RT)
2. **Extract peaks**: MINT integrates ion intensities within defined m/z and RT windows
3. **Quantify**: Peak areas or heights are calculated, proportional to metabolite abundance

**Important Note on Quantification:**
- Peak intensities reflect **relative abundance** within the same metabolite across samples
- Intensities **cannot** be compared between different metabolites (due to varying ionization efficiencies)
- For **absolute quantification**, calibration curves with known standards are required

### Data Structuring and Analysis

MINT transforms raw 3D LC-MS data into a structured table where:
- **Rows** = samples
- **Columns** = metabolites
- **Values** = peak areas/heights

This structured format enables downstream statistical analyses:
- Normalization and scaling
- Principal Component Analysis (PCA)
- Hierarchical clustering
- Statistical testing

![](image/hierarchical_clustering.png)<br/>
_**Figure 4:** Hierarchical clustering heatmap showing metabolic profiles of 12 samples from three bacterial species: _E. coli_ (EC), _S. aureus_ (SA), and _C. albicans_ (CA). Samples cluster by organism, demonstrating species-specific metabolic signatures._

## MINT Workflow Summary

1. **Create a workspace** - Organize your project files
2. **Upload LC-MS files** - Import mzML/mzXML data
3. **Add metadata** - Define sample groups, batches, and experimental conditions
4. **Define targets** - Specify metabolites with m/z and retention time windows
5. **Optimize retention times** - Use interactive tools to refine peak boundaries
6. **Run MINT** - Extract and quantify all targets across all samples
7. **Analyze results** - Visualize with heatmaps, PCA, clustering, and custom plots
8. **Export data** - Download structured tables for further statistical analysis

## Get Started

Ready to try MINT? Head to the **[Quickstart Tutorial](quickstart.md)** to process demo data in under 30 minutes, or visit the **[Installation Guide](install.md)** to set up MINT on your system.

## Citation

When using MINT in your research, please cite:

- **ms-mint library**: DOI: [10.5281/zenodo.12733875](https://zenodo.org/doi/10.5281/zenodo.12733875)
- **ms-mint-app**: DOI: [10.5281/zenodo.13121148](https://zenodo.org/doi/10.5281/zenodo.13121148)

## Support

- [GitHub: ms-mint Issues](https://github.com/LewisResearchGroup/ms-mint/issues)
- [GitHub: ms-mint-app Issues](https://github.com/LewisResearchGroup/ms-mint-app/issues)

## Contributing

MINT is an open-source project. Contributions are welcome!

- Report issues on GitHub
- Submit pull requests
- Share improvements and extensions

## Disclaimer

MINT is provided as-is. Always validate results and consult domain experts.
