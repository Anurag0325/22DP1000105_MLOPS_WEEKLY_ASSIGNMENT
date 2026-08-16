# Week 9 — Explainability, Fairness, and Drift

Files in this folder:

- **22DP1000105_Assignment_9_MAY_2026_MLOps.ipynb** — main notebook covering all tasks:
  - Task 1: Adds a synthetic `location` sensitive attribute (0/1, randomly assigned) to the IRIS
    dataset; trains a DecisionTreeClassifier on the original 4 features only (location excluded
    from training).
  - Task 2: Fairlearn `MetricFrame` — accuracy, precision, recall disaggregated by `location` group.
  - Task 3: SHAP `KernelExplainer` summary plots (full dataset, all 3 classes), with a written
    explanation of the virginica plot.
  - Task 4: Simulated production drift (petal_length offset, petal_width scaled) compared against
    the original data using `evidently`'s DataDriftPreset/DataSummaryPreset.
  - Task 5 (optional): Model card documenting intended use, performance, fairness, and limitations.

- **data.csv** — IRIS dataset used as the base training/reference data for this week's tasks
  (reused from Week 1).

- **week9_drift_report.html** — standalone HTML export of the evidently drift report generated
  in Task 4; open in a browser to view interactive drift statistics and distribution comparisons.

## Student Info

- ID: 22DP1000105
- Course: MLOps Weekly Assignment
- Week: 9
- Term: MAY 2026
