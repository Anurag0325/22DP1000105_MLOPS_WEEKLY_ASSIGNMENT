from fastapi import FastAPI, Request, HTTPException, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging, time, json
import joblib
import numpy as np

logger = logging.getLogger("iris-ml-service")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter(json.dumps({"severity":"%(levelname)s","message":"%(message)s","timestamp":"%(asctime)s"}))
handler.setFormatter(formatter)
logger.addHandler(handler)

app = FastAPI()
IRIS_CLASSES = ["setosa", "versicolor", "virginica"]
model = None

class Input(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

app_state = {"is_ready": False, "is_alive": True}

@app.on_event("startup")
async def startup_event():
    global model
    model = joblib.load("model.joblib")
    app_state["is_ready"] = True

@app.get("/live_check")
async def liveness_probe():
    if app_state["is_alive"]:
        return {"status": "alive"}
    return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.get("/ready_check")
async def readiness_probe():
    if app_state["is_ready"]:
        return {"status": "ready"}
    return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = round((time.time() - start_time) * 1000, 2)
    response.headers["X-Process-Time-ms"] = str(duration)
    return response

@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    logger.exception(json.dumps({"event":"unhandled_exception","path":str(request.url),"error":str(exc)}))
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

@app.post("/predict")
async def predict(input: Input, request: Request):
    start_time = time.time()
    try:
        input_data = input.dict()
        features = np.array([[input_data["sepal_length"], input_data["sepal_width"],
                               input_data["petal_length"], input_data["petal_width"]]])
        pred_class = int(model.predict(features)[0])
        confidence = float(np.max(model.predict_proba(features)))
        result = {"prediction": IRIS_CLASSES[pred_class], "confidence": round(confidence, 4)}
        latency = round((time.time() - start_time) * 1000, 2)
        logger.info(json.dumps({"event":"prediction","input":input_data,"result":result,"latency_ms":latency}))
        return result
    except Exception as e:
        logger.exception(json.dumps({"event":"prediction_error","error":str(e)}))
        raise HTTPException(status_code=500, detail="Prediction failed")
