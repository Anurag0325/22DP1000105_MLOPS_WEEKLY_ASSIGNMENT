import pandas as pd
import numpy as np
from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle
import os
import sys

def load_and_augment_iris(augment_size=0):
    iris = load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df['target'] = iris.target

    if augment_size > 0:
        np.random.seed(42 + augment_size)
        augmented_rows = []
        for class_id in range(3):
            class_data = df[df['target'] == class_id]
            for _ in range(augment_size):
                sample = class_data.sample(1).copy()
                for col in iris.feature_names:
                    sample[col] += np.random.normal(0, 0.05)
                augmented_rows.append(sample)
        augmented_df = pd.concat(augmented_rows, ignore_index=True)
        df = pd.concat([df, augmented_df], ignore_index=True)

    return df

def train(augment_size=0):
    os.makedirs("data", exist_ok=True)
    os.makedirs("model", exist_ok=True)

    df = load_and_augment_iris(augment_size)
    df.to_csv("data/iris.csv", index=False)
    print(f"Dataset size: {len(df)} rows")

    X = df.drop('target', axis=1)
    y = df['target']
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    clf = DecisionTreeClassifier(max_depth=3, random_state=42)
    clf.fit(X_train, y_train)

    acc = accuracy_score(y_test, clf.predict(X_test))
    print(f"Accuracy: {acc:.4f}")

    with open("model/iris_model.pkl", "wb") as f:
        pickle.dump(clf, f)

    with open("metrics.csv", "w") as f:
        f.write("accuracy\n")
        f.write(f"{acc:.4f}\n")

    print("Model saved to model/iris_model.pkl")

if __name__ == "__main__":
    augment_size = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    train(augment_size)
