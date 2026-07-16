# Landfill Methane Emission Classification

This repository contains the data-processing and machine-learning workflow used in the study:

**Landfill Methane Emission Classification from Remote Sensing Data Using Sequential Feature Selection**

## Study Overview

This study classifies landfill methane concentration levels in Indonesia using multi-source remote sensing variables and machine-learning models.

Methane concentration data were obtained from Sentinel-5P TROPOMI, while environmental predictors were derived from Sentinel-2, Sentinel-1, MODIS, and SRTM.

## Main Workflow

1. Data cleaning and preprocessing
2. Temporal split:
   - Training: 2021–2023
   - Testing: 2024
3. Methane categorization using mean ±1.5 standard deviations
4. SMOTE-Tomek resampling on the training data
5. Sequential Feature Selection
6. Hyperparameter optimization
7. Model evaluation
8. SHAP interpretation
9. Baseline comparison
10. Sensitivity analysis using:
    - Mean ±1 SD
    - Mean ±1.5 SD
    - Tertile thresholds

## Final Features

- Aerosol Optical Depth
- Elevation
- NDVI
- NDMI

## Models

- Support Vector Classification
- Random Forest
- XGBoost
- K-Nearest Neighbors
- Majority Classifier
- Stratified Dummy Classifier

## Repository Structure

- `notebooks/`: analysis notebook
- `data/`: input data or data documentation
- `outputs/`: model evaluation results
- `figures/`: figures produced by the analysis

## Reproducibility

The classification thresholds were calculated exclusively from the 2021–2023 training data and subsequently applied to the 2024 testing data.

SMOTE-Tomek was applied only to the training dataset.

## How to Run

1. Open the notebook in Google Colab.
2. Install the required libraries.
3. Load the input dataset.
4. Run all cells sequentially.

## Authors

Afi Dwi Aminurrahmah  
Nucke Widowati Kusumo Projo
