
# Quickstart Guide

Welcome to the MINT quickstart guide! This tutorial walks you through processing a complete LC-MS metabolomics dataset—from installation to analysis—in under 30 minutes. You'll learn the core MINT workflow using demo data from bacterial samples.

## 1. Install MINT

**Quick install with pip:**
```bash
pip install ms-mint-app
```

For other installation methods (conda, Docker, Windows installer), see the [Installation Guide](install.md).

**Start MINT:**
```bash
Mint
```

**Optional:** Specify a custom data directory:
```bash
Mint --data-dir /path/to/your/data
```

**First launch:**
- MINT may take 10–30 seconds to start
- Your browser will open automatically to `http://localhost:9999`
- If you see "This site can't be reached," wait for the terminal to show `INFO:waitress:Serving on http://127.0.0.1:9999`, then refresh
- On first launch, you won't have any workspaces yet

![](quickstart/first-start.png)

## 2. Create a Workspace

A **workspace** is a container for all files related to a single project. Each workspace stores MS files, metadata, target lists, and results separately.

**Steps:**
1. Navigate to the **Workspaces** tab
2. Click **CREATE WORKSPACE**
3. Enter `DEMO` as the workspace name
4. Click **CREATE**

![Create workspace](quickstart/create-workspace.png)

Your workspace is now active (shown in the blue info box at the top):

![Workspace active](quickstart/workspace-activated.png)

## 3. Download Demo Data

Download the demo dataset from [Google Drive](https://drive.google.com/drive/folders/1U4xMy5lfETk93sSVXPI79cCWyIMcAjeZ?usp=drive_link) and extract the archive.

**Dataset contents:** 

```
.
├── README.md
├── metadata
│   └── metadata.csv
├── ms-files
│   ├── CA_B1.mzXML
│   ├── CA_B2.mzXML
│   ├── CA_B3.mzXML
│   ├── CA_B4.mzXML
│   ├── EC_B1.mzXML
│   ├── EC_B2.mzXML
│   ├── EC_B3.mzXML
│   ├── EC_B4.mzXML
│   ├── SA_B1.mzML
│   ├── SA_B2.mzML
│   ├── SA_B3.mzML
│   └── SA_B4.mzML
└── targets
    └── targets.csv

4 directories, 15 files
```

**What's in the demo data?**

- **12 LC-MS files** (mzXML/mzML format) from three bacterial species:
  - _Staphylococcus aureus_ (SA) - 4 replicates
  - _Escherichia coli_ (EC) - 4 replicates
  - _Candida albicans_ (CA) - 4 replicates
  - Each replicate from one of four batches (B1–B4)

- **metadata.csv** - Sample information including organism labels, batches, and experimental conditions

- **targets.csv** - Target list with metabolite m/z values and retention times (metabolites were previously identified)

## 4. Upload LC-MS Files

**Steps:**
1. Navigate to the **MS-Files** tab
2. Drag and drop all 12 MS files into the upload area (or click to browse)
3. Wait for upload to complete

![](quickstart/ms-files-uploaded.png)

**Optional but recommended:** Convert files to Feather format for faster processing:
- Select all files
- Click **CONVERT SELECTED FILES TO FEATHER**
- This creates optimized `.feather` files and removes the original mzML/mzXML files

## 5. Add Metadata

Metadata links your MS files to experimental conditions (sample groups, batches, quality control designations, etc.). This is **essential** for meaningful analysis.

**Steps:**
1. Navigate to the **Metadata** tab
2. Upload `metadata.csv`
3. Review the populated table

![](quickstart/metadata-added.png)

**Why metadata matters:**
- Enables grouping and coloring in visualizations
- Controls which samples are used for optimization
- Tracks batch effects and quality control samples
- Powers statistical comparisons between groups

| Column Name           | Description                                                                                                                                   |
|-----------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| `ms_file_label`       | The label of the mass spectrometry file.                                                                                                      |
| `color`               | Color coding for visual identification.                                                                                                       |
| `use_for_optimization`| Boolean value indicating if the file is used in peak optimization.                                                                             |
| `in_analysis`         | Indicates if the sample is included in the analysis.                                                                                          |
| `label`               | Group of the sample (e.g., treatment group vs. control group).                                                                                |
| `sample_type`         | Type of the sample, default is `Biological Sample`, other labels could be `Standard Sample` or `Quality Control`.                             |
| `run_order`           | Order in which the samples were processed (1-N).                                                                                              |
| `plate`               | Batch ID, for example, the plate if samples come from multiple plates.                                                                        |
| `plate_row`           | Row location of the sample on the plate (e.g., 1-12 for a 96-well plate).                                                                     |
| `plate_column`        | Column location of the sample on the plate (e.g., A-H for a 96-well plate).                                                                   |
| `ms_column`           | Mass spectrometry column information.                                                                                                         |
| `ionization_mode`     | Mode of ionization used in the mass spectrometry.                                                                                             |


## 6. Add Targets (Metabolites)

The **target list** defines which metabolites to extract from your LC-MS data. Each target specifies an m/z value and retention time window.

**Steps:**
1. Navigate to the **Targets** tab
2. Upload `targets.csv` (or `MINT-targets.csv`)
3. Review the target table

![](quickstart/targets-table.png)

**Important notes:**
- The same extraction protocol is applied to all files
- MINT is designed for **targeted** analysis (not untargeted peak picking)
- Requires stable chromatography and consistent retention times
- See [Target Lists documentation](targets.md) for target file format details 

## 7. Optimize Retention Times

Retention times can drift between runs due to column aging or temperature variations. MINT's optimization tools help you verify and adjust retention time windows.

**Steps:**
1. Navigate to the **Peak Optimization** tab
2. In **File selection**, choose `Use all files` (for this small demo dataset)
   - *For large datasets:* Select a representative subset including QC/standard samples
3. Click **UPDATE PEAK PREVIEWS**

![](quickstart/peak-preview.png)

**What you're seeing:**
- Peak shapes for all targets across selected files
- Colors match those in your metadata table
- Validates that targets are correctly defined and present in your samples

**Manual optimization (optional):**

Use the interactive tool below the previews to fine-tune individual targets:

![](quickstart/peak-optimization.png)

- **Zoom** to the region of interest
- **SET RT TO CURRENT VIEW** - Updates the retention time window (green box)
- **CONFIRM RETENTION TIME** - Sets expected RT to center of current view
- **REMOVE TARGET** - Delete targets not present in your samples

The black vertical line shows the expected RT from your target list for comparison with previous experiments.

When satisfied with all peak shapes, proceed to **Processing**.

## 8. Process the Data

Now run the full data extraction across all samples and targets.

**Steps:**
1. Navigate to the **Processing** tab
2. Click **RUN MINT**
3. Wait for the progress bar to complete
4. A green notification will appear: `Finished running MINT`

![](quickstart/run-mint.png)

**Download results:**
- **DOWNLOAD ALL RESULTS** - Complete dataset in tidy (long) format
- **DOWNLOAD DENSE MATRIX** - Peak values in matrix format (samples × metabolites)
  - Select which metric to export (e.g., `peak_max`, `peak_area`)
  - Option to transpose the matrix


## 9. Analyze the Results

Once processing completes, you can explore your data with MINT's built-in visualization tools.

### Heatmap

Navigate to the **Heatmap** tab to see an interactive heatmap of your results.

**Customization options:**
- Cluster rows/columns
- Show dendrograms
- Transpose matrix
- Calculate correlations between metabolites
- Filter by sample type

Resize your browser window and click **UPDATE** to regenerate the plot.

### Analysis/Plotting Tool

The **Analysis/Plotting** tab provides a powerful interface for creating custom visualizations using [Seaborn](https://seaborn.pydata.org/).

**Let's create a simple bar plot:**

1. Navigate to **Analysis/Plotting**
2. Default settings create a basic bar plot showing average peak intensities:

![](quickstart/01-demo-plot.png)

3. **Improve the plot step-by-step:**
   - Set **X axis** to `peak_label`
   - Set **Aspect ratio** to `5`
   - Enable **Logarithmic y-scale**
   - Click **UPDATE**

![](quickstart/02-demo-plot.png)

4. **Create faceted plots by group:**
   - Set **Figure height** to `1.5`
   - Set **Aspect ratio** to `2`
   - Set **Column** to `Label` (organism)
   - Set **Row** to `Batch`
   - Click **UPDATE**

![](quickstart/03-demo-plot.png)

This creates a grid showing all metabolites across all organisms and batches simultaneously!

**Challenge:** Try to recreate this plot:

![](quickstart/05-demo-plot.png)

*Hint: Experiment with different plot types (violin, box, strip) and color/hue settings.*

## Next Steps

Congratulations! You've completed the MINT quickstart tutorial. You now know how to:
- ✅ Install and launch MINT
- ✅ Create workspaces and upload data
- ✅ Define targets and optimize retention times
- ✅ Process LC-MS data
- ✅ Visualize and analyze results

**Learn more:**
- [GUI Documentation](gui.md) - Complete interface reference
- [Target Lists](targets.md) - Target file format details
- [GitHub Issues](https://github.com/LewisResearchGroup/ms-mint-app/issues) - Report bugs or request features
- [Lewis Research Group Software](https://www.lewisresearchgroup.org/software) - Other metabolomics tools
