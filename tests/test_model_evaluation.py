import os
import pandas as pd
import pytest
import mlflow
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score

MODEL_URI = "models:/iris-classifier@champion"
DATA_PATH = "data.csv"
FEATURE_COLUMNS = ["sepal_length", "sepal_width", "petal_length", "petal_width"]
MIN_ACCURACY = 0.85
MIN_PRECISION = 0.80
MIN_RECALL = 0.80

@pytest.fixture(scope="module")
def model():
    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:8100")
    mlflow.set_tracking_uri(tracking_uri)
    return mlflow.pyfunc.load_model(MODEL_URI)

@pytest.fixture(scope="module")
def eval_data():
    df = pd.read_csv(DATA_PATH)
    X = df[FEATURE_COLUMNS]
    y = df["species"]
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    return X_test, y_test

@pytest.fixture(scope="module")
def predictions(model, eval_data):
    X_test, _ = eval_data
    return model.predict(X_test)

def test_model_loads(model):
    assert model is not None

def test_prediction_output_shape(predictions, eval_data):
    _, y_test = eval_data
    assert len(predictions) == len(y_test)

def test_sanity_prediction_on_samples(model):
    samples = pd.DataFrame(
        [[5.1, 3.5, 1.4, 0.2], [6.0, 2.7, 5.1, 1.6], [6.9, 3.1, 5.4, 2.1]],
        columns=FEATURE_COLUMNS,
    )
    preds = model.predict(samples)
    assert len(preds) == 3
    for p in preds:
        assert p in {"setosa", "versicolor", "virginica"}

def test_accuracy_above_threshold(predictions, eval_data):
    _, y_test = eval_data
    acc = accuracy_score(y_test, predictions)
    assert acc >= MIN_ACCURACY

def test_precision_above_threshold(predictions, eval_data):
    _, y_test = eval_data
    prec = precision_score(y_test, predictions, average="macro", zero_division=0)
    assert prec >= MIN_PRECISION

def test_recall_above_threshold(predictions, eval_data):
    _, y_test = eval_data
    rec = recall_score(y_test, predictions, average="macro", zero_division=0)
    assert rec >= MIN_RECALL
