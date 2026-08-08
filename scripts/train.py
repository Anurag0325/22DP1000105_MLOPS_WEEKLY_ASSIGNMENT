import argparse
import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

FEATURE_COLS = ["sepal length (cm)", "sepal width (cm)", "petal length (cm)", "petal width (cm)"]
LABEL_COL = "target"
RANDOM_SEED = 42
EXPERIMENT_NAME = "iris-mlsecops-poisoning"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--poison-level", type=int, required=True)
    parser.add_argument("--data", default="data/iris.csv")
    args = parser.parse_args()

    df = pd.read_csv(args.data)
    X, y = df[FEATURE_COLS], df[LABEL_COL]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_SEED, stratify=y
    )

    mlflow.set_experiment(EXPERIMENT_NAME)
    with mlflow.start_run(run_name=f"poison_{args.poison_level}pct"):
        mlflow.log_param("poison_level", args.poison_level)
        mlflow.log_param("model", "DecisionTreeClassifier")
        mlflow.log_param("n_train", len(X_train))
        mlflow.log_param("n_test", len(X_test))

        model = DecisionTreeClassifier(random_state=RANDOM_SEED)
        model.fit(X_train, y_train)
        preds = model.predict(X_test)

        metrics = {
            "accuracy": accuracy_score(y_test, preds),
            "precision": precision_score(y_test, preds, average="weighted", zero_division=0),
            "recall": recall_score(y_test, preds, average="weighted", zero_division=0),
            "f1_score": f1_score(y_test, preds, average="weighted", zero_division=0),
        }
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(model, artifact_path="model")
        print(f"[poison={args.poison_level}%] " + ", ".join(f"{k}={v:.4f}" for k, v in metrics.items()))


if __name__ == "__main__":
    main()
