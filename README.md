# Week 4 - CI Integration with IRIS Pipeline

## Overview
Extends the Week 3 IRIS classification pipeline by integrating Continuous Integration using GitHub Actions. Every push and pull request automatically pulls versioned data and models via DVC, runs a pytest suite covering data validation and model evaluation, and publishes the results as a CML report comment.

## Repository Structure
```
.
├── .dvc/
│   └── config                     # DVC remote configuration
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions CI workflow
├── data/
│   └── iris.csv.dvc               # DVC pointer for IRIS dataset
├── model/
│   └── iris_model.pkl.dvc         # DVC pointer for trained model
├── tests/
│   ├── test_data_validation.py    # Data schema, nulls, dtype, range checks
│   └── test_model_evaluation.py   # Model sanity, accuracy, precision, recall checks
├── train.py                       # Training script with data augmentation
├── metrics.csv                    # Accuracy metrics from latest training run
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## Setup Instructions

### 1. Clone the repository
```
git clone https://github.com/Anurag0325/22DP1000105_MLOPS_WEEKLY_ASSIGNMENT.git
cd 22DP1000105_MLOPS_WEEKLY_ASSIGNMENT
git checkout week_4
```

### 2. Create virtual environment
```
python3 -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
pip install dvc dvc-gs pytest scikit-learn pandas numpy
```

### 3. Pull data and model from GCS
```
dvc pull
```

### 4. Run the test suite locally
```
pytest tests/ -v
```

## CI Pipeline (GitHub Actions)

The workflow at `.github/workflows/ci.yml` runs automatically on:
- Every `push`, on any branch
- Every `pull_request`, on any branch
- Manual trigger via `workflow_dispatch` (Actions tab -> Run workflow)

### Pipeline Steps
1. Checkout the repository
2. Set up Python 3.12 and install dependencies
3. Authenticate to GCP using Workload Identity Federation
4. `dvc pull` - fetch versioned `data/iris.csv` and `model/iris_model.pkl` from the GCS remote
5. Run the full `pytest` suite (13 tests across data validation and model evaluation)
6. Publish the test report via CML:
   - As a **PR comment** when triggered by a pull request
   - As a **commit comment** when triggered by a direct push
7. Fail the job if any test fails, blocking a broken merge

## Authentication: Workload Identity Federation

This project's GCP organization enforces `constraints/iam.disableServiceAccountKeyCreation`, which blocks creating downloadable JSON service account keys. Instead, GitHub Actions authenticates via Workload Identity Federation:

| Component | Value |
|---|---|
| Workload Identity Pool | `github-pool` |
| Workload Identity Provider | `github-provider` |
| Service Account | `github-ci-dvc@project-eac74fb9-0e15-492a-ab1.iam.gserviceaccount.com` |
| Service Account Role | `roles/storage.objectAdmin` |
| Trust scoped to | `Anurag0325/22DP1000105_MLOPS_WEEKLY_ASSIGNMENT` |

No long-lived keys or secrets are stored in GitHub. GitHub's OIDC identity token is exchanged for short-lived GCP credentials at runtime.

## DVC Remote
- **Backend:** Google Cloud Storage
- **Bucket:** `gs://mlops-course-project-eac74fb9-0e15-492a-ab1-v4-unique/dvc-store`

## Test Suite

### `tests/test_data_validation.py`
| Test | Checks |
|---|---|
| `test_file_not_empty` | Dataset has rows |
| `test_expected_columns_present` | All required columns exist |
| `test_no_missing_values` | No nulls in feature/target columns |
| `test_feature_dtypes_numeric` | Feature columns are numeric |
| `test_feature_value_ranges` | Feature values fall within plausible bounds |
| `test_target_values_valid` | Target is one of {0, 1, 2} |
| `test_target_is_integer_type` | Target column is integer-typed |

### `tests/test_model_evaluation.py`
| Test | Checks |
|---|---|
| `test_model_loads` | Model file loads correctly |
| `test_prediction_output_shape` | Predictions match test set size |
| `test_sanity_prediction_on_samples` | Predicts correct-looking classes on representative samples |
| `test_accuracy_above_threshold` | Accuracy >= 0.85 |
| `test_precision_above_threshold` | Macro precision >= 0.80 |
| `test_recall_above_threshold` | Macro recall >= 0.80 |

## Key Commands Reference

| Command | Description |
|---|---|
| `dvc pull` | Pull tracked data/model files from GCS remote |
| `pytest tests/ -v` | Run the full validation + evaluation test suite |
| `git push origin week_4` | Push changes, triggering CI automatically |
| `gh pr create` (or GitHub UI) | Open a pull request from `week_4` into `main` |
| `cml comment create report.md` | (used inside CI) Publish test report as PR/commit comment |

## Branch History
- `week_1` - Initial IRIS pipeline on Vertex AI
- `week_2` - DVC integration with GCS remote, data versioning (v1.0-v3.0)
- `week_3` - Feast feature store integration
- `week_4` - CI integration: pytest suite, GitHub Actions with DVC pull via Workload Identity Federation, CML reporting, merged to `main` via pull request

## Student Info
- **ID:** 22DP1000105
- **Course:** MLOps Weekly Assignment
- **Week:** 4
- **Term:** MAY 2026
