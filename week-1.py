# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.3
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
# ! pip3 install --upgrade --quiet  google-cloud-aiplatform

# %%
PROJECT_ID = "project-eac74fb9-0e15-492a-ab1"
LOCATION = "us-central1"

# %%
BUCKET_NAME = "mlops-course-project-eac74fb9-0e15-492a-ab1-v4-unique"
BUCKET_URI = f"gs://{BUCKET_NAME}"

# %%
MODEL_ARTIFACT_DIR="iris_classifier/model"

# %%
from google.cloud import aiplatform

aiplatform.init(project=PROJECT_ID, location=LOCATION, staging_bucket=BUCKET_URI)

# %%
import os
import sys

# %%
import pandas as pd

# %%
df = pd.read_csv("data.csv")

# %%
df.head()

# %% [markdown]
# # Task 2

# %%
from google.cloud import storage

# %%
client = storage.Client(project=PROJECT_ID)

# %%
bucket = client.bucket(BUCKET_NAME)
if not bucket.exists():
    bucket = client.create_bucket(BUCKET_NAME, location=LOCATION)
    print(f"✅ Bucket created: {BUCKET_NAME}")
else:
    print(f"✅ Bucket already exists: {BUCKET_NAME}")

# %%
from sklearn.model_selection import train_test_split

# %%
train, test = train_test_split(df, test_size = 0.4, stratify = df['species'], random_state = 42)

# %%
# Split and upload train/eval
train.to_csv("iris_train.csv", index=False)
test.to_csv("iris_eval.csv", index=False)

# %%
bucket.blob("data/iris_train.csv").upload_from_filename("iris_train.csv")
bucket.blob("data/iris_eval.csv").upload_from_filename("iris_eval.csv")

# %%
print("✅ Train and eval data uploaded to GCS!")
print(f"   → gs://{BUCKET_NAME}/data/iris_train.csv")
print(f"   → gs://{BUCKET_NAME}/data/iris_eval.csv")

# %%
X_train = train[['sepal_length','sepal_width','petal_length','petal_width']]

# %%
y_train = train.species

# %%
X_test = test[['sepal_length','sepal_width','petal_length','petal_width']]

# %%
y_test = test.species

# %%
print(train.columns.tolist())

# %%
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn import metrics

# %%
mod_dt = DecisionTreeClassifier(max_depth = 3, random_state = 1)

# %%
mod_dt.fit(X_train,y_train)

# %%
prediction=mod_dt.predict(X_test)

# %%
print('The accuracy of the Decision Tree is',"{:.3f}".format(metrics.accuracy_score(prediction,y_test)))

# %%
import pickle
import json
from datetime import datetime
from google.cloud import storage

# %%
TIMESTAMP = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
ARTIFACT_DIR = f"artifacts/{TIMESTAMP}"
print(f"🕐 Run timestamp: {TIMESTAMP}")

# %%
client = storage.Client(project=PROJECT_ID)
bucket = client.bucket(BUCKET_NAME)

# %%
bucket.blob("data/iris_train.csv").download_to_filename("iris_train.csv")
bucket.blob("data/iris_eval.csv").download_to_filename("iris_eval.csv")

# %%
train_df = pd.read_csv("iris_train.csv")
eval_df  = pd.read_csv("iris_eval.csv")

# %%
X_train = train_df[['sepal_length','sepal_width','petal_length','petal_width']]
y_train = train_df['species']
X_eval  = eval_df[['sepal_length','sepal_width','petal_length','petal_width']]
y_eval  = eval_df['species']

# %%
model = DecisionTreeClassifier(max_depth=3, random_state=1)
model.fit(X_train, y_train)
print("✅ Model trained!")

# %%
predictions = model.predict(X_eval)
accuracy = metrics.accuracy_score(y_eval, predictions)
print(f"✅ Accuracy: {accuracy:.3f}")

# %%
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

# %%
log = {
    "timestamp": TIMESTAMP,
    "accuracy": accuracy,
    "model": "DecisionTreeClassifier",
    "max_depth": 3,
    "train_size": len(train_df),
    "eval_size": len(eval_df)
}

# %%
with open("training_log.json", "w") as f:
    json.dump(log, f, indent=2)

# %%
bucket.blob(f"{ARTIFACT_DIR}/model.pkl").upload_from_filename("model.pkl")
bucket.blob(f"{ARTIFACT_DIR}/training_log.json").upload_from_filename("training_log.json")

# %%
print(f"✅ Artifacts saved to gs://{BUCKET_NAME}/{ARTIFACT_DIR}/")
print(f"   → model.pkl")
print(f"   → training_log.json")

# %%
LATEST_ARTIFACT_DIR = ARTIFACT_DIR

# %% [markdown]
# # Inference

# %%
client = storage.Client(project=PROJECT_ID)
bucket = client.bucket(BUCKET_NAME)

# %%
print(f"📦 Loading model from: gs://{BUCKET_NAME}/{LATEST_ARTIFACT_DIR}/model.pkl")
bucket.blob(f"{LATEST_ARTIFACT_DIR}/model.pkl").download_to_filename("model_loaded.pkl")

# %%
with open("model_loaded.pkl", "rb") as f:
    loaded_model = pickle.load(f)

# %%
bucket.blob("data/iris_eval.csv").download_to_filename("iris_eval.csv")
eval_df = pd.read_csv("iris_eval.csv")

# %%
X_eval = eval_df[['sepal_length','sepal_width','petal_length','petal_width']]
y_eval = eval_df['species']

# %%
predictions = loaded_model.predict(X_eval)
accuracy = metrics.accuracy_score(y_eval, predictions)

# %%
print("✅ Inference complete!")
print(f"   Accuracy on eval set: {accuracy:.3f}")

# %%
results = eval_df.copy()
results['predicted'] = predictions
print(results[['species','predicted']].head(10).to_string())

# %% [markdown]
# # Second Run

# %%
client = storage.Client(project=PROJECT_ID)
bucket = client.bucket(BUCKET_NAME)
blobs = client.list_blobs(BUCKET_NAME, prefix="artifacts/")
for blob in blobs:
    print(blob.name)

# %%
