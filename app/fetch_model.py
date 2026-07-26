import mlflow
import os
import pickle

mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
MODEL_URI = "models:/iris-classifier@champion"

print(f"Fetching model from {MODEL_URI}")
model = mlflow.sklearn.load_model(MODEL_URI)

with open("iris_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Saved model to iris_model.pkl")
