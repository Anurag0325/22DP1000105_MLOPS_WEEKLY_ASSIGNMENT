# 22DP1000105 — Assignment 5 (MLOps): MLflow Integration

This assignment integrates **MLflow** into the IRIS classification pipeline for experiment tracking and model registry, replacing the DVC-based model tracking used in earlier weeks. DVC continues to be used for data versioning only in prior weeks' history; this week's `data.csv` is tracked directly in git.

## Repo Info

- **Branch:** `week_5`
- **MLflow experiment:** `iris-hpo`
- **MLflow registered model:** `iris-classifier`
- **Champion alias:** `champion`

## Files in This Repository

| File | Purpose |
|---|---|
| `22DP1000105_Assignment_5_MAY_2026_MLOps.ipynb` | Main notebook — runs the hyperparameter sweep, logs all runs to MLflow, registers the best model and tags it `champion`, and evaluates that champion model by loading it from the MLflow registry. |
| `data.csv` | Input dataset — columns `sepal_length, sepal_width, petal_length, petal_width, species` (species is a string label, no encoding needed). |
| `tests/test_champion_model.py` | Pytest sanity check — loads the champion model via `models:/iris-classifier@champion` and confirms it loads and predicts correctly. Used in CI (Task 6). |
| `tests/test_model_evaluation.py` | Pytest suite — loads the champion model from the registry and evaluates it against `data.csv`, asserting accuracy/precision/recall exceed set thresholds. |
| `.github/workflows/champion-model-ci.yml` | GitHub Actions workflow — on every push to `week_5` (or manual trigger), fetches the champion model from the MLflow registry and runs `tests/test_champion_model.py` against it. |
| `.gitignore` | Excludes local model binaries (`model/`), joblib artifacts, notebook checkpoints, and environment/cache files from version control. |
| `README.md` | This file. |

## MLflow Tracking Server

Runs on the same GCP Compute Engine VM backing the Vertex AI Workbench instance, inside a `screen` session so it persists across SSH disconnects:

```bash
screen -S mlflow_execution

mlflow server --host 0.0.0.0 --port 8100 \
  --backend-store-uri sqlite:////home/$(whoami)/mlflow.db \
  --allowed-hosts "localhost,127.0.0.1,<EXTERNAL_IP>,<EXTERNAL_IP>:8100,localhost:8100,127.0.0.1:8100" \
  --cors-allowed-origins "*"
```

- Requires firewall rule `allow-mlflow` (ingress, tcp:8100, source `0.0.0.0/0`).
- **The external IP is ephemeral** and changes on instance restart. Check with `curl -s ifconfig.get me` and update `--allowed-hosts` plus the GitHub Actions repo variable `MLFLOW_TRACKING_URI` if it changes.
- UI: `http://<EXTERNAL_IP>:8100`
- The notebook connects via `mlflow.set_tracking_uri("http://localhost:8100")`.

## What Was Done

1. **Hyperparameter sweep** — `RandomForestClassifier` over `n_estimators ∈ {50,100,200} × max_depth ∈ {2,4,None}` (9 combinations), computing accuracy/precision/recall/F1 for each.
2. **MLflow tracking** — each combination logged as an MLflow run (`mlflow.log_params`, `mlflow.log_metrics`, `mlflow.sklearn.log_model` with `infer_signature`). The best run by macro-F1 was registered as `iris-classifier` and tagged with the alias `champion`.
3. **UI comparison** — runs compared side-by-side in the MLflow Tracking UI (parallel-coordinates and table views) to confirm the champion run was among the best performers.
4. **DVC model tracking removed** — the model artifact is no longer tracked by DVC; it's tracked exclusively through the MLflow Model Registry.
5. **Registry-based evaluation** — the evaluation cell and `tests/test_model_evaluation.py` load the model via `mlflow.pyfunc.load_model("models:/iris-classifier@champion")` instead of a local or DVC path.
6. **CI via GitHub Actions** — `champion-model-ci.yml` fetches the champion model from the registry and runs a pytest sanity check on every push, using `MLFLOW_TRACKING_URI` as a repo Actions variable.

## Incident & Recovery (worth noting)

Partway through this assignment, the Workbench VM's ephemeral external IP changed after an instance restart, which also terminated the `screen` session running the MLflow server — silently wiping the SQLite-backed experiment/registry data along with it (a fresh, empty `mlflow.db` was effectively in use). This caused GitHub Actions CI to fail with `RESOURCE_DOES_NOT_EXIST: Registered Model with name=iris-classifier not found`.

**Fix:** restarted the MLflow server with the new IP added to `--allowed-hosts`, updated the `MLFLOW_TRACKING_URI` repo variable to match, and re-ran the sweep/logging/registration notebook cells to repopulate the experiment and re-tag the champion alias. CI was re-triggered and passed afterward.

**Takeaway:** a SQLite-backed MLflow server on a single ephemeral VM is fine for coursework, but isn't resilient to VM restarts — a production setup would need a persistent backend store (e.g. a managed database) and a stable server address.

## Reproducing This Assignment

1. Ensure the MLflow tracking server is running on the VM (see above) and note the current external IP.
2. Open the notebook and run all cells top to bottom.
3. Open the MLflow UI at `http://<EXTERNAL_IP>:8100` to inspect `iris-hpo` and `iris-classifier`.
4. Run tests locally:
```bash
   MLFLOW_TRACKING_URI=http://localhost:8100 pytest tests/ -v
```
5. Push to `week_5` (or trigger manually) to run CI.
