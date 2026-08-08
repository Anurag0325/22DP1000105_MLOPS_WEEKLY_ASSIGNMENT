# Week 8 — MLSecOps: Data Poisoning on the IRIS Pipeline

## Files
| File | Purpose |
|---|---|
| `scripts/poison_iris.py` | Task 2 — overwrites `data/iris.csv` from `data/iris_clean_master.csv` at a given corruption % (0/5/10/50). Replaces all 4 features with random out-of-range values and assigns a random class label for the selected fraction of rows. |
| `scripts/train.py` | Task 3 — trains a `DecisionTreeClassifier` on the current `data/iris.csv`, logs `poison_level` as a param and accuracy/precision/recall/f1 as metrics to MLflow (experiment `iris-mlsecops-poisoning`). |
| `scripts/compare_results.py` | Task 4 — pulls all 4 MLflow runs into `data/comparison_table.csv` and `data/degradation_plot.png`. |
| `data/iris_clean_master.csv` | Untouched clean baseline, source for every poisoned variant. |
| `data/iris.csv` + `data/iris.csv.dvc` | DVC-tracked, one commit per poison level (0/5/10/50%) — see git log for lineage. |
| `data/comparison_table.csv`, `data/degradation_plot.png` | Task 4 outputs. |

## Run order
```bash
source myenv/bin/activate
export MLFLOW_TRACKING_URI=sqlite:///mlflow.db

python scripts/poison_iris.py --pct <N>       # N = 0, 5, 10, or 50
dvc add data/iris.csv
git add data/iris.csv.dvc && git commit -m "Poisoning N% of input data" && dvc push
python scripts/train.py --poison-level <N>
git push origin week_8

mlflow ui --backend-store-uri sqlite:///mlflow.db --host 0.0.0.0 --port 8080
python scripts/compare_results.py
```

## Results

| Poison % | Accuracy | Precision | Recall | F1 |
|---|---|---|---|---|
| 0  | 0.9697 | 0.9722 | 0.9697 | 0.9696 |
| 5  | 0.9545 | 0.9598 | 0.9545 | 0.9543 |
| 10 | 0.8788 | 0.8831 | 0.8788 | 0.8786 |
| 50 | 0.7121 | 0.7063 | 0.7121 | 0.7075 |

## Task 1 — ML Threat Vectors (explained in screencast)
Covered: data poisoning (data ingestion/training), backdoor injection (training),
adversarial examples (inference), model extraction (inference API), prompt
injection (LLM inference) — stage, mechanism, and a real-world example for each.

## Task 4 — Analysis
- Noticeable degradation begins at 5% (96.97% → 95.45%); the sharp drop is
  between 10% and 50% (87.88% → 71.21%).
- All four metrics move together here since poisoning is untargeted
  (random features + random label), affecting all three classes roughly evenly.
- At 50% corruption the model still scores 71.21% accuracy — well above the
  33% chance floor for 3 balanced classes — so it's still learning real signal
  from the remaining ~50% clean data, not behaving randomly.

## Task 5 — Mitigation & Data Quantity vs. Quality (explained in screencast)
- **Detection/mitigation**: schema validation (range/type checks before
  training), statistical/drift profiling against a trusted reference
  distribution, anomaly detection (e.g. isolation forest) on incoming samples,
  DVC-based data provenance (as demonstrated here — each poison level is a
  separate, hash-verified commit), and a held-out validation set never
  sourced from the same ingestion pipeline.
- **Quantity vs. quality**: more data does not compensate for a fixed
  *poisoned ratio* — doubling a dataset that's 10% poisoned still leaves it
  10% poisoned. What matters is the clean-data ratio, not raw volume; cleaning
  before scaling is the effective lever. The 50% run above is the empirical
  case — quantity alone can't rescue a pipeline once quality drops past a
  threshold; contaminated data must be filtered first.

## Student Info

* ID: 22DP1000105
* Course: MLOps Weekly Assignment
* Week: 8
* Term: MAY 2026
