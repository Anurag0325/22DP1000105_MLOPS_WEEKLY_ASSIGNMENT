import os
import mlflow
import pandas as pd

def test_champion_model_loads_and_predicts():
    tracking_uri = os.environ["MLFLOW_TRACKING_URI"]
    mlflow.set_tracking_uri(tracking_uri)
    model = mlflow.pyfunc.load_model("models:/iris-classifier@champion")
    sample = pd.DataFrame([{
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2,
    }])
    preds = model.predict(sample)
    assert preds is not None
    assert len(preds) == 1
    assert preds[0] in {"setosa", "versicolor", "virginica"}
