# 22DP1000105 - MLOps Weekly Assignment - Week 1

## Problem Statement
Build an end-to-end IRIS classifier ML pipeline on Google Cloud Platform using Vertex AI and Google Cloud Storage.

## Approach
1. Set up Vertex AI Workbench instance on GCP
2. Upload IRIS dataset to GCS bucket (train/eval split)
3. Train DecisionTree classifier fetching data from GCS
4. Save model artifacts to GCS organized by execution timestamp
5. Run inference fetching trained model from GCS

## Files
| File | Description |
|------|-------------|
| `22DP1000105_Assignment_1_MAY_2026_MLOps.ipynb` | Main notebook with complete pipeline |
| `data.csv` | Raw IRIS dataset |
| `.gitignore` | Excludes binary/data files from git |

## GCS Bucket Structure
gs://mlops-course-project-eac74fb9-0e15-492a-ab1-v4-unique/
├── data/
│   ├── iris_train.csv
│   └── iris_eval.csv
└── artifacts/
    ├── 2026-06-22T17-35-00/
    ├── 2026-06-22T17-40-45/
    └── 2026-06-22T17-44-55/

## Results
- Model: DecisionTreeClassifier (max_depth=3)
- Accuracy: 0.951
- Training Runs: 3 separate runs with timestamped artifact folders

## Learnings
- Setting up and navigating GCP and Vertex AI Workbench
- Using GCS for ML data and artifact management
- Building reproducible ML pipelines with timestamp-based artifact organization
- Separating training and inference into distinct scripts
