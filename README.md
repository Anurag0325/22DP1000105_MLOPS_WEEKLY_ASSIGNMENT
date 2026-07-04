# Week 3 MLOps Assignment — Feast Feature Store Integration with IRIS Pipeline

**Roll Number:** 22DP1000105  
**Branch:** week_3  
**Repository:** 22DP1000105_MLOPS_WEEKLY_ASSIGNMENT  
**Term:** SEPT 2025  

---

## Objective

Add a Feast Feature Store layer to the IRIS classification pipeline so that training and inference share a single, consistent source of engineered features — eliminating training/serving skew.

---

## Repository Structure

```
22DP1000105_MLOPS_WEEKLY_ASSIGNMENT/
├── feature_repo/
│   ├── feature_store.yaml              # Task 1: Feast config (local SQLite backend)
│   ├── iris_repo.py                    # Task 2: Entity, FileSource, FeatureView definitions
│   ├── data/
│   │   ├── iris_data_adapted_for_feast.csv     # Raw IRIS dataset with timestamps
│   │   ├── iris_data_adapted_for_feast.parquet # Parquet version for Feast FileSource
│   │   ├── registry.db                         # Created by feast apply (Task 3)
│   │   └── online_store.db                     # Created by feast materialize (Task 3)
│   └── bq/
│       ├── feature_store.yaml          # Task 6: Feast config (BigQuery backend)
│       └── iris_repo_bq.py             # Task 6: BigQuerySource feature definitions
├── iris_model.joblib                   # Task 4: Trained LogisticRegression model
├── iris_label_encoder.joblib           # Task 4: LabelEncoder for species
├── iris_data_adapted_for_feast.csv     # Source dataset
└── 22DP1000105.ipynb                   # Main notebook (all tasks)
```

---

## Dataset

**File:** `iris_data_adapted_for_feast.csv`  
**Source:** IITMBSMLOps GitHub (branch: week_3)

The standard IRIS dataset is modified to be Feast-compatible:
- 3 iris plants tracked over 15 days (Sep 17 – Oct 1, 2025)
- `iris_id`: unique entity identifier (1001, 1002, 1003)
- `event_timestamp`: when measurement was recorded (required by Feast)
- `created_timestamp`: when record was ingested
- Features: `sepal_length`, `sepal_width`, `petal_length`, `petal_width`
- Label: `species` (setosa, versicolor, virginica)

---

## Tasks Completed

### Task 1 — Initialize Feast Feature Repository
- Created `feature_repo/` directory following Feast conventions
- Configured `feature_store.yaml` with:
  - **Offline store**: file-based (Parquet + point-in-time joins)
  - **Online store**: SQLite (local, zero-config)
  - **Registry**: SQLite file at `data/registry.db`

### Task 2 — Define Entities, Data Sources & Feature Views
Defined in `feature_repo/iris_repo.py`:
- **Entity**: `iris_id` (INT64) — unique identifier for each iris plant
- **FileSource**: points to local Parquet file with `event_timestamp` and `created_timestamp`
- **FeatureView**: `iris_features` — groups all 4 measurement columns + species, TTL = 365 days

### Task 3 — Apply Definitions & Materialize Features
- Ran `feast apply` → registered entity and feature view in SQLite registry
- Ran `feast materialize-incremental` → pushed latest feature values per `iris_id` into SQLite online store
- Verified: 3 rows in online store (one per iris_id), feature view state = `AVAILABLE_ONLINE`

### Task 4 — Fetch Features for Training (Offline Store)
**Key behavioral change:** Model no longer reads CSV directly.
- Built entity dataframe (`iris_id` + `event_timestamp`)
- Called `get_historical_features()` → Feast performs point-in-time join → returns (45, 7) dataframe
- Trained `LogisticRegression` on Feast output
- Test accuracy: **1.0000**
- Saved `iris_model.joblib` and `iris_label_encoder.joblib`

### Task 5 — Fetch Features for Inference (Online Store)
- Called `get_online_features()` for iris_ids [1001, 1002, 1003]
- Feast performs low-latency lookup against SQLite online store
- Model predictions:
  - iris_id 1001 → `versicolor` ✅
  - iris_id 1002 → `setosa` ✅
  - iris_id 1003 → `setosa` ✅
- Consistency check: Feast online features match raw CSV ground truth = **True**

### Task 6 (Optional) — BigQuery Backend
- Created BigQuery dataset: `feast_iris_feature_store`
- Loaded 45 rows into BigQuery table: `iris_features`
- Configured separate `feature_repo/bq/` with BigQuery offline store
- Ran `feast apply` against BigQuery
- Successfully retrieved (45, 7) training dataframe from BigQuery via `get_historical_features()`

---

## How to Run

### Prerequisites
```bash
pip install feast scikit-learn joblib google-cloud-bigquery
```

### Steps
```bash
# 1. Clone the repo and switch to week_3 branch
git clone https://github.com/Anurag0325/22DP1000105_MLOPS_WEEKLY_ASSIGNMENT.git
cd 22DP1000105_MLOPS_WEEKLY_ASSIGNMENT
git checkout week_3

# 2. Convert CSV to Parquet
python3 -c "
import pandas as pd
df = pd.read_csv('feature_repo/data/iris_data_adapted_for_feast.csv')
df['event_timestamp'] = pd.to_datetime(df['event_timestamp'], utc=True)
df['created_timestamp'] = pd.to_datetime(df['created_timestamp'], utc=True)
df.to_parquet('feature_repo/data/iris_data_adapted_for_feast.parquet', index=False)
"

# 3. Apply Feast definitions
cd feature_repo && feast apply

# 4. Materialize features to online store
feast materialize-incremental $(date -u +%Y-%m-%dT%H:%M:%S)

# 5. Run the notebook 22DP1000105.ipynb for Tasks 4 and 5
```

---

## Key Concept: Why Feast?

| Without Feast | With Feast |
|---------------|------------|
| Training reads CSV directly | Training reads from offline store via `get_historical_features()` |
| Inference duplicates transformation logic | Inference reads from online store via `get_online_features()` |
| Risk of training/serving skew | Single source of truth for both paths |

---

## Environment
- **Platform**: GCP Vertex AI Workbench
- **Python**: 3.12
- **Feast**: 0.64.0
- **Offline Store**: File-based (Tasks 1-5), BigQuery (Task 6)
- **Online Store**: SQLite
