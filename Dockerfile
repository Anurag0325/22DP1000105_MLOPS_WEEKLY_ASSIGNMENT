FROM python:3.11-slim
WORKDIR /app
COPY app/ .
RUN pip install --no-cache-dir -r requirements.txt

ARG MLFLOW_TRACKING_URI
ENV MLFLOW_TRACKING_URI=${MLFLOW_TRACKING_URI}
RUN python fetch_model.py

EXPOSE 8200
CMD ["uvicorn", "iris_fastapi:app", "--host", "0.0.0.0", "--port", "8200"]
