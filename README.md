markdown

# Week 5 - MLflow Integration with IRIS Pipeline

## Overview
Extends the Week 2 IRIS classification pipeline (DVC-based data/model
versioning) by integrating MLflow for experiment tracking and a model
registry. Model artifacts are now logged, versioned, and served through
MLflow instead of DVC; DVC continues to track data files only.

## Repository Structure
    .
    ├── .dvc/
    │   └── config                  # DVC remote configuration
    ├── data/
    │   └── iris.csv.dvc            # DVC pointer for IRIS dataset
    ├── mlruns/                     # Local MLflow tracking store (if used)
    ├── train.py                    # Training script with hyperparameter tuning + MLflow logging
    ├── evaluate.py                 # Evaluation script - loads model from MLflow Registry
    ├── metrics.csv                 # Accuracy metrics from latest training run
    ├── requirements.txt            # Python dependencies
    └── README.md                   # This file

## Setup Instructions

**1. Clone the repository**

    git clone https://github.com/Anurag0325/22DP1000105_MLOPS_WEEKLY_ASSIGNMENT.git
    cd 22DP1000105_MLOPS_WEEKLY_ASSIGNMENT
    git checkout week_5

**2. Create virtual environment**

    python3 -m venv .env
    source .env/bin/activate
    pip install dvc dvc-gs scikit-learn pandas numpy mlflow

**3. Pull data from GCS (models are no longer stored in DVC)**

    dvc pull

**4. Start the MLflow Tracking Server / UI**

    mlflow ui --host 0.0.0.0 --port 5000

Open http://localhost:5000 (or the GCP VM's external IP:5000) to view
the Tracking UI.

## Training Script

train.py loads the IRIS dataset, runs hyperparameter tuning across
multiple configurations, and logs each run's parameters, metrics, and
trained model to MLflow.

    python train.py --n_estimators 50  --max_depth 3
    python train.py --n_estimators 100 --max_depth 5
    python train.py --n_estimators 150 --max_depth 7

Each run is logged as a new MLflow experiment run with:
- **Params:** n_estimators, max_depth (and any other tuned hyperparameters)
- **Metrics:** accuracy, precision, recall, f1
- **Artifact:** the trained model, logged via `mlflow.sklearn.log_model`

## Model Registry

After comparing runs in the Tracking UI, the best-performing run's
model is registered:

    mlflow models register -m runs:/<RUN_ID>/model -n iris_classifier

Or via the UI: **Run details → Register Model → iris_classifier**

## Evaluation Script

evaluate.py fetches the model directly from the MLflow Model Registry
by name and version, rather than from DVC or a local path.

    python evaluate.py --model_name iris_classifier --model_version latest

```python
import mlflow

model = mlflow.pyfunc.load_model(f"models:/iris_classifier/latest")
```

## DVC Remote

- **Backend:** Google Cloud Storage
- **Bucket:** gs://mlops-course-project-eac74fb9-0e15-492a-ab1-v4-unique/dvc-store
- **Scope:** data files only (model tracking removed in this week's assignment)

## Experiment Comparison

|
 Run 
|
 n_estimators 
|
 max_depth 
|
 Accuracy 
|
|
-----
|
--------------
|
-----------
|
----------
|
|
 1   
|
 50           
|
 3         
|
 TBD      
|
|
 2   
|
 100          
|
 5         
|
 TBD      
|
|
 3   
|
 150          
|
 7         
|
 TBD      
|

See the MLflow Tracking UI for the full side-by-side comparison
charts and tables.

## Key MLflow Commands

|
 Command                                   
|
 Description                                  
|
|
--------------------------------------------
|
-----------------------------------------------
|
|
 mlflow ui                                  
|
 Launch the Tracking UI                        
|
|
 mlflow.start_run()                         
|
 Begin a new tracked run                       
|
|
 mlflow.log_param / log_params              
|
 Log hyperparameter(s)                         
|
|
 mlflow.log_metric / log_metrics            
|
 Log evaluation metric(s)                      
|
|
 mlflow.sklearn.log_model                   
|
 Log the trained model as an artifact          
|
|
 mlflow models register                     
|
 Register a model version in the Model Registry
|
|
 mlflow.pyfunc.load_model("models:/name/v") 
|
 Load a registered model by name/version       
|

## CI Integration (Optional - Task 6)

The GitHub Actions workflow (`.github/workflows/ci.yml`) fetches the
latest/best model from the MLflow Model Registry and runs sanity
checks against it, replacing the previous DVC-based model retrieval
step.

## Student Info
- **ID:** 22DP1000105
- **Course:** MLOps Weekly Assignment
- **Week:** 5
- **Term:** MAY 2026



