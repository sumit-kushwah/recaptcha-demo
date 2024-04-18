import argparse
import os
import sys
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
import mlflow

parser = argparse.ArgumentParser(description="Data Preparation")

parser.add_argument("--input", type=str, help="Clean Input folder", required=True)
parser.add_argument(
    "--output", type=str, help="Processed Output file path", required=True
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

input_file = os.path.join(args.input, "processed_data.csv")
output_path = args.output
mlflow_tracking_uri = args.mlflow_uri
experiment_name = args.mlflow_exp

if os.path.exists(input_file):
    print(f"Input file found: {input_file}")
    input_file = os.path.abspath(input_file)
else:
    print(f"Input file not found: {input_file}")
    sys.exit(1)


if os.path.exists(output_path):
    print(f"Output file found: {output_path}")
else:
    print(f"Output path not found: {output_path}")
    print("Creating output path")
    os.makedirs(output_path, exist_ok=True)

output_path = os.path.abspath(output_path)

df = pd.read_csv(input_file)

# Data Preparation
X = df.drop("Annual Turnover", axis=1)
y = df["Annual Turnover"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

mlflow.set_tracking_uri(mlflow_tracking_uri)
mlflow.set_experiment(experiment_name)

with mlflow.start_run(run_name="Data Preparation") as run:
    mlflow.set_tag("release.version", "1.0.0")
    mlflow.log_param("Input file path", input_file)
    mlflow.log_param("Rows Before", df.shape[0])
    mlflow.log_param("Columns Before", df.shape[1])

    mlflow.log_param("Train Test Split", 0.2)
    mlflow.log_param("Random State", 42)
    mlflow.log_param("X_train", X_train.shape)
    mlflow.log_param("X_test", X_test.shape)
    mlflow.log_param("y_train", y_train.shape)
    mlflow.log_param("y_test", y_test.shape)

    X_train_path = os.path.join(output_path, "X_train.csv")
    X_test_path = os.path.join(output_path, "X_test.csv")
    y_train_path = os.path.join(output_path, "y_train.csv")
    y_test_path = os.path.join(output_path, "y_test.csv")

    X_train.to_csv(X_train_path, index=False)
    X_test.to_csv(X_test_path, index=False)
    y_train.to_csv(y_train_path, index=False)
    y_test.to_csv(y_test_path, index=False)

    mlflow.log_artifact(X_train_path)
    mlflow.log_artifact(X_test_path)
    mlflow.log_artifact(y_train_path)
    mlflow.log_artifact(y_test_path)
    print("Data Preparation Completed")
