## Student Info

* ID: 22DP1000105
* Course: MLOps Weekly Assignment
* Week: 7
* Term: MAY 2026

# Week 7 — Stress Testing, Observability & Scaling (IRIS Pipeline)

## Files
- `app/train.py` — trains a DecisionTreeClassifier on the real IRIS dataset, saves `model.joblib`
- `app/main.py` — FastAPI serving app: `/predict`, `/live_check`, `/ready_check`, structured JSON logging
- `app/requirements.txt`, `app/Dockerfile` — image build for the API
- `k8s/deployment.yaml` — Deployment with CPU/memory requests & limits (required for HPA)
- `k8s/service.yaml` — LoadBalancer Service exposing `/predict`
- `k8s/hpa.yaml` — HorizontalPodAutoscaler, minReplicas=1, maxReplicas=3, target CPU 50%
- `stress-test/post.lua` — wrk payload script (POST body for `/predict`)
- `stress-test/task2_baseline.txt` — wrk output, single pod, 1200 connections
- `stress-test/task3_hpa_3replicas.txt` — wrk output with HPA active, max 3 replicas
- `stress-test/task4_load_with_logs.txt` — same load test, correlated with Cloud Logging output
- `stress-test/task4_logs.json` — Cloud Logging pull (`gcloud logging read`) during Task 4 test
- `stress-test/task5_hpa_1replica.txt` — wrk output with HPA capped at 1 replica, 2000 connections
- `.github/workflows/ci.yml` — CI/CD: builds image, pushes to Artifact Registry, deploys to GKE, runs wrk stress test

## How to reproduce
1. `cd app && python train.py` — trains model
2. `docker build -t iris-api:latest .` — build image
3. Push to Artifact Registry, `kubectl apply -f k8s/` — deploy
4. `wrk -t4 -c1200 -d60s --latency -s stress-test/post.lua http://<EXTERNAL_IP>/predict`

## Key findings (Task 5 vs Task 3)
| Metric | max=3, c=1200 | max=1, c=2000 |
|---|---|---|
| Connect errors | 183 | 983 |
| Pod restarts during test | 1 | 2 |
| Requests/sec | ~51-55 | ~51 |

Single-worker Uvicorn under high concurrency causes CPU saturation, failed liveness/readiness
probes, and pod restarts. With maxReplicas=3, other pods continue serving during a restart;
with maxReplicas=1, every restart is a full outage window.

## Learnings
- HPA requires `resources.requests` on the deployment or it can't compute utilization
- Small GKE nodes (2 vCPU) get most capacity consumed by system add-ons — lowered pod CPU
  request from 250m to 100m so 3 replicas could co-schedule
- A newly created/recreated HPA object can get stuck reporting `<unknown>` metrics even when
  metrics-server is healthy; recreating the HPA resource resolved it
- Single Uvicorn worker is the real bottleneck — under load it can't serve health probes in time
