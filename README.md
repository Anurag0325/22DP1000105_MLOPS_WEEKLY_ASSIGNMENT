# Week 6 — Continuous Deployment for IRIS Inference API

This branch (`week_6`) contains the CD pipeline that containerizes the IRIS
inference API, pushes it to Google Artifact Registry, and deploys it to
Google Kubernetes Engine (GKE) — fully automated via GitHub Actions.

## Files in this branch

| File | Purpose |
|---|---|
| `app/iris_fastapi.py` | FastAPI inference service. Loads `iris_model.pkl` and exposes `/` and `/predict/` endpoints on port 8200. |
| `app/requirements.txt` | Python dependencies for the API (FastAPI, uvicorn, scikit-learn, pandas, mlflow). |
| `app/fetch_model.py` | Build-time script that pulls the current **champion** model from the MLflow Model Registry and saves it as `iris_model.pkl` inside the image (Task 6). |
| `Dockerfile` | Builds the API image: installs dependencies, runs `fetch_model.py` to bundle the MLflow champion model, exposes port 8200, and starts uvicorn. |
| `k8s/deployment.yaml` | Kubernetes Deployment manifest — 2 replicas of the `iris-api` container on port 8200, with a readiness probe on `/`. |
| `k8s/service.yaml` | Kubernetes Service (`LoadBalancer`) exposing the Deployment on port 80, routed to container port 8200. |
| `.github/workflows/cd.yaml` | GitHub Actions workflow: builds the Docker image (fetching the MLflow model at build time), pushes it to Artifact Registry, then deploys it to the GKE cluster. |

Note: `app/iris_model.pkl` is intentionally **not** committed to this repo
(see `.gitignore`) — it is fetched fresh from the MLflow Model Registry
during the Docker build, so the container never depends on a stale local
copy.

## Task summary

**Task 1 — Pod vs Container**
Explained in the video screencast: a Docker container is one running
instance of an image; a Kubernetes Pod is the smallest deployable unit in
K8s and wraps one or more containers that share networking/storage.
Kubernetes schedules, scales, and heals Pods, not raw containers.

**Task 2 — Dockerfile for the IRIS API**
`app/iris_fastapi.py` serves predictions via FastAPI on port 8200.
`Dockerfile` packages it with all dependencies. Verified locally with
`docker build` + `docker run` + `curl` against `/predict/`.

**Task 3 — GCP Service Account**
Service account `github-cd-deployer` created with:
- `roles/artifactregistry.writer`
- `roles/container.developer`
- `roles/iam.serviceAccountUser`

Authenticated via Workload Identity Federation (pool `github-pool`,
provider `github-provider`) — no service account key files used.
Configured as GitHub Actions secrets: `GCP_PROJECT_ID`, `GCP_WIF_PROVIDER`,
`GCP_SA_EMAIL`.

**Task 4 — Build & Push via GitHub Actions**
`.github/workflows/cd.yaml` (`build-and-push` job) builds the Docker image
and pushes it to Artifact Registry repo `my-repo` in `us-central1`, tagged
with the commit SHA.

**Task 5 — Deploy to GKE**
`.github/workflows/cd.yaml` (`deploy` job) authenticates to the
`test-iris-v1` GKE cluster (`us-central1-a`), substitutes the freshly built
image tag into `k8s/deployment.yaml`, and applies both manifests. Verified
with `kubectl get pods` / `kubectl get service` and a live `curl` against
the LoadBalancer's external IP, returning correct predictions
(e.g. `{"predicted_class":"setosa"}`).

**Task 6 (Optional) — MLflow Model in the Container**
`app/fetch_model.py` connects to the MLflow tracking server, loads the
model registered as `iris-classifier` under the `champion` alias via
`mlflow.sklearn.load_model()`, and re-serializes it as `iris_model.pkl`
during the Docker build (`RUN python fetch_model.py`). The deployed API
serves predictions using this registry-sourced model with no MLflow access
required at runtime.

## Known limitation

The MLflow tracking server used for Task 6 runs on a Vertex AI Workbench
instance rather than a persistent managed service, and the instance
auto-stops after a period of idle time. This means:
- The MLflow server (and its external IP) must be running whenever the
  GitHub Actions workflow builds the image, since `fetch_model.py` needs
  live access to the registry at build time.
- The `MLFLOW_TRACKING_URI` GitHub Actions **variable** must be updated if
  the Workbench VM's external IP changes after a restart.

This is a reasonable tradeoff for an assignment environment; a production
setup would host MLflow as a persistent service (e.g. Cloud Run or a
dedicated always-on VM with a static IP) instead.

## Reproducing locally

```bash
cd app && cd ..
docker build --build-arg MLFLOW_TRACKING_URI=<mlflow_server_url> -t iris-api .
docker run -d -p 8200:8200 iris-api
curl -X POST "http://localhost:8200/predict/" -H "Content-Type: application/json" \
  -d '{"sepal_length":5.1,"sepal_width":3.5,"petal_length":1.4,"petal_width":0.2}'
```
