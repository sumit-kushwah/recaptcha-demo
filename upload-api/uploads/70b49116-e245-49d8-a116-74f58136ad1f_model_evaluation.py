import argparse
import os
import sys
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import mlflow

parser = argparse.ArgumentParser(description="Model Training")

parser.add_argument("--x-test-path", type=str, help="X test path file", required=True)
parser.add_argument("--y-test-path", type=str, help="y test path file", required=True)
parser.add_argument(
    "--model-file-path", type=str, help="Model File Path", required=True
)
parser.add_argument(
    "--mlflow_uri",
    type=str,
    help="MLFlow Tracking URI",
    default="http://localhost:8080",
)

parser.add_argument(
    "--mlflow_exp",
    type=str,
    help="MLFlow Experiment Name",
)

args = parser.parse_args()

x_test_path = os.path.join(args.x_test_path, "X_test.csv")
y_test_path = os.path.join(args.y_test_path, "y_test.csv")
model_file_path = os.path.join(args.model_file_path, "model.pkl")
mlflow_tracking_uri = args.mlflow_uri
experiment_name = args.mlflow_exp

if os.path.exists(x_test_path):
    print(f"x train path found: {x_test_path}")
    input_file = os.path.abspath(x_test_path)
else:
    print(f"Input file not found: {x_test_path}")
    sys.exit(1)

if os.path.exists(y_test_path):
    print(f"x train path found: {y_test_path}")
    input_file = os.path.abspath(y_test_path)
else:
    print(f"Input file not found: {y_test_path}")
    sys.exit(1)

if os.path.exists(model_file_path):
    print(f"x train path found: {model_file_path}")
    input_file = os.path.abspath(model_file_path)
else:
    print(f"Input file not found: {model_file_path}")
    sys.exit(1)

X_test = pd.read_csv(x_test_path)
y_test = pd.read_csv(y_test_path)

# load model using joblib
import joblib

model = joblib.load(model_file_path)

y_pred = model.predict(X_test)

from sklearn.metrics import mean_squared_error
import numpy as np

rmse = np.sqrt(mean_squared_error(y_test, y_pred))

# MLFlow tracking setup
mlflow.set_tracking_uri(mlflow_tracking_uri)
mlflow.set_experiment(experiment_name)

with mlflow.start_run(run_name="Model Evaluation") as run:
    mlflow.set_tag("release.version", "1.0.0")
    mlflow.log_param("X test file path", x_test_path)
    mlflow.log_param("y test file path", y_test_path)
    mlflow.log_param("Model file path", model_file_path)
    mlflow.log_metric("RMSE", rmse)
