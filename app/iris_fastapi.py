from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import pandas as pd

app = FastAPI(title="Iris Classifier API")

with open("iris_model.pkl", "rb") as f:
    model = pickle.load(f)

FEATURE_NAMES = ["sepal_length", "sepal_width", "petal_length", "petal_width"]

class IrisInput(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

@app.get("/")
def read_root():
    return {"message": "Welcome to the Iris Classifier API!"}

@app.post("/predict/")
def predict_species(data: IrisInput):
    input_df = pd.DataFrame(
        [[data.sepal_length, data.sepal_width, data.petal_length, data.petal_width]],
        columns=FEATURE_NAMES,
    )
    prediction = model.predict(input_df)[0]
    return {"predicted_class": str(prediction)}
