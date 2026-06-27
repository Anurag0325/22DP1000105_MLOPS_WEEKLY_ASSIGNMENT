# Week 2 - DVC Integration with IRIS Pipeline

## Overview

Extends the Week 1 IRIS classification pipeline by integrating DVC
to version both data and model artifacts backed by Google Cloud Storage.

## Repository Structure

    .
    ├── .dvc/
    │   └── config                  # DVC remote configuration
    ├── data/
    │   └── iris.csv.dvc            # DVC pointer for IRIS dataset
    ├── model/
    │   └── iris_model.pkl.dvc      # DVC pointer for trained model
    ├── train.py                    # Training script with data augmentation
    ├── metrics.csv                 # Accuracy metrics from latest training run
    ├── requirements.txt            # Python dependencies
    └── README.md                   # This file

## Setup Instructions

**1. Clone the repository**

    git clone https://github.com/Anurag0325/22DP1000105_MLOPS_WEEKLY_ASSIGNMENT.git
    cd 22DP1000105_MLOPS_WEEKLY_ASSIGNMENT
    git checkout week_2

**2. Create virtual environment**

    python3 -m venv .env
    source .env/bin/activate
    pip install dvc dvc-gs scikit-learn pandas numpy

**3. Pull data and model from GCS**

    dvc pull

## Training Script

train.py loads the IRIS dataset, optionally augments it with synthetic
samples, trains a DecisionTreeClassifier, and saves the model and metrics.

    python train.py 0    # Iteration 1 - base dataset (150 rows)
    python train.py 30   # Iteration 2 - augmented dataset (240 rows)
    python train.py 60   # Iteration 3 - augmented dataset (330 rows)

## DVC Remote

- **Backend:** Google Cloud Storage
- **Bucket:** gs://mlops-course-project-eac74fb9-0e15-492a-ab1-v4-unique/dvc-store

## Data Versions

| Tag  | Rows | Description               |
|------|------|---------------------------|
| v1.0 | 150  | Base IRIS dataset         |
| v2.0 | 240  | Augmented (+30 per class) |
| v3.0 | 330  | Augmented (+60 per class) |

## Switching Between Versions

Switch to a previous version using a tag:

    git checkout v1.0
    dvc checkout

Return to the latest version:

    git checkout week_2
    dvc checkout

## Key DVC Commands

| Command            | Description                              |
|--------------------|------------------------------------------|
| dvc init           | Initialize DVC in repo                   |
| dvc remote list    | Show configured remotes                  |
| dvc add file       | Track a file with DVC                    |
| dvc push           | Push tracked files to GCS remote         |
| dvc pull           | Pull tracked files from GCS remote       |
| dvc checkout       | Restore files to match .dvc pointers     |
| dvc status         | Show sync status between local and remote|

## Student Info

- **ID:** 22DP1000105
- **Course:** MLOps Weekly Assignment
- **Week:** 2
- **Term:** MAY 2026
