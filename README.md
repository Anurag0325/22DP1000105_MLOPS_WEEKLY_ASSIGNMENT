# Week 7 — Stress Testing, Observability & Scaling (IRIS Pipeline)

This branch (week_7) contains a stress-testing and observability setup for the IRIS inference API — load testing with wrk, Horizontal Pod Autoscaling on GKE, and correlating scaling/failure behavior with GCP Cloud Monitoring and Cloud Logging.

## Files in this branch

| File | Purpose |
|---|---|
| `app/train.py` | Trains a DecisionTreeClassifier on the real IRIS dataset and saves `model.joblib`. |
| `app/main.py` | FastAPI inference service. Loads `model.joblib` and exposes `/predict`, `/live_check`, `/ready_check` with structured JSON logging. |
| `app/requirements.txt` | Python dependencies for the API. |
| `app/Dockerfile` | Builds the API image; trains the model at build time so `model.joblib` is never committed. |
| `k8s/deployment.yaml` | Deployment manifest with CPU/memory `requests`/`limits` (required for HPA to compute utilization). |
| `k8s/service.yaml` | LoadBalancer Service exposing the Deployment on port 80, routed to container port 8080. |
| `k8s/hpa.yaml` | HorizontalPodAutoscaler — minReplicas=1, maxReplicas=3, target CPU utilization 50%. |
| `stress-test/post.lua` | wrk Lua script — POST payload for `/predict`. |
| `stress-test/task2_baseline.txt` | wrk output: single pod, 1200 connections (no HPA scaling effect yet). |
| `stress-test/task3_hpa_3replicas.txt` | wrk output with HPA active, scaled to 3 replicas. |
| `stress-test/task4_load_with_logs.txt` | Same load test, correlated with live Cloud Logging output. |
| `stress-test/task4_logs.json` | Cloud Logging pull (`gcloud logging read`) captured during the Task 4 test window. |
| `stress-test/task5_hpa_1replica.txt` | wrk output with HPA capped at maxReplicas=1, 2000 connections. |
| `.github/workflows/ci.yml` | CI/CD workflow: builds the Docker image, pushes to Artifact Registry, deploys to GKE, then runs a wrk stress test against the live endpoint. |

## Task summary

**Task 1 — CI/CD with Stress Testing:** Extended `.github/workflows/ci.yml` with a `stress-test` job that runs after `build-and-deploy`, installing wrk on the runner and load-testing the live `/predict` endpoint automatically on every push.

**Task 2 — High-Concurrency Load with wrk:** Ran `wrk -t4 -c1200 -d30s` against the single-pod deployment. All requests timed out (`timeout 3300+`, socket connect errors), establishing the pre-HPA baseline.

**Task 3 — Horizontal Pod Autoscaler:** Configured `k8s/hpa.yaml` (min=1, max=3, target CPU 50%). Reran the same wrk test; HPA correctly scaled to 3 replicas (confirmed via `kubectl get hpa` / `kubectl get pods`), though a single Uvicorn worker per pod still caused one pod to fail its liveness probe and restart mid-test.

**Task 4 — GCP Cloud Monitoring & Logging:** Watched GKE Workloads/Observability tabs for CPU per pod during the same load test, and used Logs Explorer (`resource.type="k8s_container" resource.labels.container_name="iris-api"`) to confirm a pod shutdown/restart cycle (`Application shutdown complete` → `Started server process`) correlating exactly with the liveness-probe failure seen via `kubectl describe pod`.

**Task 5 — Bottleneck Under Constrained Scaling:** Patched HPA to `maxReplicas: 1` and doubled load to `wrk -c2000`. Connect errors rose from 183 to 983, and the single pod restarted twice (vs. once with 3 replicas available), demonstrating that HPA's benefit here is resilience/failover, since raw single-worker throughput was the underlying constraint in both scenarios.

## Key findings (Task 5 vs Task 3)

| Metric | max=3, c=1200 | max=1, c=2000 |
|---|---|---|
| Connect errors | 183 | 983 |
| Pod restarts during test | 1 | 2 |
| Requests/sec | ~51–55 | ~51 |

## Known limitations / learnings

- HPA requires `resources.requests` on the Deployment or it cannot compute CPU utilization at all.
- The GKE cluster's default nodes (2 vCPU) had most capacity already consumed by system add-ons (`gmp-system`, `kube-state-metrics`, etc.); lowered the pod's CPU request from 250m to 100m so all 3 HPA replicas could co-schedule.
- A freshly created HPA object occasionally got stuck reporting `<unknown>` metrics even though `metrics-server` and `kubectl top` worked fine; recreating the HPA resource under a new name resolved it.
- The single Uvicorn worker process is the real application-level bottleneck — under high concurrency it cannot service health-check probes in time, regardless of replica count.

## Reproducing locally

```bash
cd app && python train.py
docker build -t iris-api:latest .
docker tag iris-api:latest <REGION>-docker.pkg.dev/<PROJECT_ID>/iris-repo/iris-api:latest
docker push <REGION>-docker.pkg.dev/<PROJECT_ID>/iris-repo/iris-api:latest
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
wrk -t4 -c1200 -d60s --latency -s stress-test/post.lua http://<EXTERNAL_IP>/predict
```

## Student Info

* ID: 22DP1000105
* Course: MLOps Weekly Assignment
* Week: 7
* Term: MAY 2026
