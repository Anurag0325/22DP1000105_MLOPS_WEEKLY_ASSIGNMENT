import pickle
import pandas as pd
import pytest
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score

MODEL_PATH = "model/iris_model.pkl"
DATA_PATH = "data/iris.csv"

FEATURE_COLUMNS = [
    "sepal length (cm)",
    "sepal width (cm)",
    "petal length (cm)",
    "petal width (cm)",
]

MIN_ACCURACY = 0.85
MIN_PRECISION = 0.80
MIN_RECALL = 0.80


@pytest.fixture(scope="module")
def model():
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)


@pytest.fixture(scope="module")
def eval_data():
    df = pd.read_csv(DATA_PATH)
    X = df[FEATURE_COLUMNS]
    y = df["target"]
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
    assert len(predictions) == len(y_test), "Prediction count doesn't match test set size"


def test_sanity_prediction_on_samples(model):
    samples = pd.DataFrame(
        [
            [5.1, 3.5, 1.4, 0.2],
            [6.0, 2.7, 5.1, 1.6],
            [6.9, 3.1, 5.4, 2.1],
        ],
        columns=FEATURE_COLUMNS,
    )
    preds = model.predict(samples)
    assert len(preds) == 3
    for p in preds:
        assert p in (0, 1, 2), f"Unexpected predicted class: {p}"


def test_accuracy_above_threshold(predictions, eval_data):
    _, y_test = eval_data
    acc = accuracy_score(y_test, predictions)
    print(f"Accuracy: {acc:.4f}")
    assert acc >= MIN_ACCURACY, f"Accuracy {acc:.4f} is below minimum threshold {MIN_ACCURACY}"


def test_precision_above_threshold(predictions, eval_data):
    _, y_test = eval_data
    prec = precision_score(y_test, predictions, average="macro", zero_division=0)
    print(f"Precision: {prec:.4f}")
    assert prec >= MIN_PRECISION, f"Precision {prec:.4f} is below minimum threshold {MIN_PRECISION}"


def test_recall_above_threshold(predictions, eval_data):
    _, y_test = eval_data
    rec = recall_score(y_test, predictions, average="macro", zero_division=0)
    print(f"Recall: {rec:.4f}")
    assert rec >= MIN_RECALL, f"Recall {rec:.4f} is below minimum threshold {MIN_RECALL}"
