# 22DP1000105 — Assignment 5 (MLOps): MLflow Integration

This assignment extends the Week 4 pipeline by replacing DVC-based model tracking with **MLflow** for experiment tracking, model registry, and CI-based model validation.

## Repo Info

- **Branch:** `week_5`
- **Notebook:** `22DP1000105_Assignment_5_MAY_2026_MLOps.ipynb`
- **Data:** `data.csv` — columns `sepal_length, sepal_width, petal_length, petal_width, species` (string label, no encoding required)
- **MLflow experiment:** `iris-hpo`
- **MLflow registered model:** `iris-classifier`
- **Champion alias:** `champion`

## Environment

- GCP Vertex AI Workbench instance: `instance-20260621-144156`
- Notebook kernel: `/opt/micromamba/envs/jupyterlab/bin/python3`
- Terminal shell: `base` micromamba environment (`/opt/micromamba/bin/python3.12`)

> **Note on environments:** the Jupyter kernel (`jupyterlab` env) and the terminal shell (`base` env) are separate Python environments on this VM. Packages installed in one are not automatically available in the other. `mlflow` was installed into the kernel with `!{sys.executable} -m pip install mlflow`; `dvc` and `pytest` were installed into the `base` env directly via `pip install` in the terminal. Keep this in mind when re-running any part of the pipeline.

## MLflow Tracking Server

Run on the same Compute Engine VM backing this Workbench instance, inside a `screen` session so it persists across SSH disconnects:

```bash
screen -S mlflow_execution

mlflow server --host 0.0.0.0 --port 8100 \
  --backend-store-uri sqlite:////home/$(whoami)/mlflow.db \
  --allowed-hosts "localhost,127.0.0.1,<EXTERNAL_IP>,<EXTERNAL_IP>:8100,localhost:8100,127.0.0.1:8100" \
  --cors-allowed-origins "*"
```

- Firewall rule `allow-mlflow` (ingress, tcp:8100, source `0.0.0.0/0`) must exist on the VM's network.
- The external IP is **ephemeral** — it changes on instance restart. Before relying on the server (running the notebook, CI, or recording the demo video), check it with:
  ```bash
  curl -s ifconfig.me
  ```
  and update `--allowed-hosts` and the `MLFLOW_TRACKING_URI` GitHub Actions variable (see below) if it has changed.
- UI: `http://<EXTERNAL_IP>:8100`
- The notebook connects via `mlflow.set_tracking_uri("http://localhost:8100")` since it runs on the same VM as the server.

## What Changed This Week

### Task 1 — Hyperparameter sweep
Ran a grid search with `RandomForestClassifier` over `n_estimators ∈ {50, 100, 200}` × `max_depth ∈ {2, 4, None}` (9 combinations), computing accuracy, precision, recall, and F1 for each.

### Task 2 — MLflow experiment tracking and model registration
- Wrapped each sweep combination in `mlflow.start_run()`.
- Logged hyperparameters (`mlflow.log_params`), metrics (`mlflow.log_metrics`), and the trained model (`mlflow.sklearn.log_model` with `infer_signature`).
- Selected the best run by macro-F1 and registered it as `iris-classifier` via `mlflow.register_model()`.
- Tagged the winning version with the alias `champion` via `client.set_registered_model_alias(...)`.

### Task 3 — Compare experiments in the MLflow UI
Opened the `iris-hpo` experiment in the MLflow UI, selected multiple runs, and used the Compare view (parallel-coordinates and table) to visually confirm the champion run was among the best performers across the hyperparameter grid.

### Task 4 — Removed model tracking from DVC
Since the model is now tracked via the MLflow Model Registry, DVC no longer needs to track the model artifact:
```bash
dvc remove model/iris_model.pkl.dvc
echo "model/" >> .gitignore
```
`data/iris.csv.dvc` remains under DVC tracking — only the model artifact tracking was removed. There was no `dvc.yaml` pipeline in this repo (models were tracked via plain `dvc add`, not a pipeline stage), so no pipeline edits were needed.

### Task 5 — Evaluation via MLflow registry
The evaluation cell now loads the champion model directly from the registry instead of a local or DVC-tracked path:
```python
import mlflow

mlflow.set_tracking_uri("http://localhost:8100")
champion_model = mlflow.pyfunc.load_model("models:/iris-classifier@champion")
```
Predictions are generated on the full dataset and standard classification metrics (accuracy, macro precision/recall/F1) are printed for a sanity check.

### Task 6 — CI: model sanity check via GitHub Actions
A workflow (`.github/workflows/champion-model-ci.yml`) fetches the champion model from the MLflow registry and runs a pytest sanity check (`tests/test_champion_model.py`) on every push to `week_5`, and can also be triggered manually via `workflow_dispatch`.

- **Repo variable required:** `MLFLOW_TRACKING_URI`, set under **Settings → Secrets and variables → Actions → Variables**, pointing at `http://<EXTERNAL_IP>:8100`.
- **Reachability requirement:** the MLflow server must be running and its external IP reachable at the time CI runs, since GitHub Actions connects to it over the public internet. If the VM has restarted or the IP has changed since the variable was last set, CI will fail on a connection error rather than a test failure — update the `MLFLOW_TRACKING_URI` variable and `--allowed-hosts` accordingly.

To run the same check locally:
```bash
MLFLOW_TRACKING_URI=http://localhost:8100 pytest tests/test_champion_model.py -v
```

## Repository Structure (relevant additions/changes)

```
.
├── 22DP1000105_Assignment_5_MAY_2026_MLOps.ipynb
├── data.csv
├── data/
│   └── iris.csv.dvc
├── model/                                # git-ignored; no longer DVC-tracked
├── tests/
│   ├── test_data_validation.py
│   ├── test_model_evaluation.py
│   └── test_champion_model.py            # new — validates champion model from registry
├── .github/
│   └── workflows/
│       └── champion-model-ci.yml         # new — CI sanity check against MLflow registry
├── .gitignore                            # updated — model/ added
├── requirements.txt
├── train.py
└── README.md
```

## Reproducing This Assignment

1. Ensure the MLflow tracking server is running on the VM (see above) and note its current external IP.
2. Open `22DP1000105_Assignment_5_MAY_2026_MLOps.ipynb` and run all cells top to bottom.
3. Open the MLflow UI at `http://<EXTERNAL_IP>:8100` to inspect the `iris-hpo` experiment and the `iris-classifier` registered model.
4. Run the local test suite, including the champion model check:
   ```bash
   pytest tests/ -v
   ```
5. Push to `week_5` to trigger the CI workflow, or trigger it manually from the **Actions** tab.

## Known Limitations

- The MLflow tracking server's external IP is ephemeral and tied to the current VM session; it is not a persistent, production-grade deployment.
- CI depends on the VM and MLflow server being live at run time — this is acceptable for the scope of this assignment but would need a managed/persistent tracking server for real production use.
