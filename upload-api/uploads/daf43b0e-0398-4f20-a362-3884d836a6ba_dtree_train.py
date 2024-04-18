import argparse
import os
import sys
import pandas as pd
from sklearn.model_selection import train_test_split
import mlflow

parser = argparse.ArgumentParser(description="Model Training")

parser.add_argument("--x-train-path", type=str, help="X train folder", required=True)
parser.add_argument("--y-train-path", type=str, help="y train folder", required=True)
parser.add_argument("--model-out-dir", type=str, help="Model Directory", required=True)
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

x_train_path = os.path.join(args.x_train_path, "X_train.csv")
y_train_path = os.path.join(args.y_train_path, "y_train.csv")
model_path = args.model_out_dir
mlflow_tracking_uri = args.mlflow_uri
experiment_name = args.mlflow_exp

if os.path.exists(x_train_path):
    print(f"x train path found: {x_train_path}")
    input_file = os.path.abspath(x_train_path)
else:
    print(f"Input file not found: {x_train_path}")
    sys.exit(1)

if os.path.exists(y_train_path):
    print(f"x train path found: {y_train_path}")
    input_file = os.path.abspath(y_train_path)
else:
    print(f"Input file not found: {y_train_path}")
    sys.exit(1)


if os.path.exists(model_path):
    print(f"Output file found: {model_path}")
else:
    print(f"Output path not found: {model_path}")
    print("Creating output path")
    os.makedirs(model_path, exist_ok=True)

model_path = os.path.abspath(model_path)

X_train = pd.read_csv(x_train_path)
y_train = pd.read_csv(y_train_path)


# MLFlow tracking setup
mlflow.set_tracking_uri(mlflow_tracking_uri)
mlflow.set_experiment(experiment_name)


# Model Training
mlflow.autolog()

from sklearn.tree import DecisionTreeRegressor

model = DecisionTreeRegressor(random_state=42, max_depth=5)

with mlflow.start_run(run_name="Model Training(Decision Tree)") as run:
    model.fit(X_train, y_train)

    # Save the model
    model_file = os.path.join(model_path, "model.pkl")
    import joblib

    from matplotlib import pyplot as plt
    from sklearn import tree

    tree.plot_tree(model)
    mlflow.log_figure(plt.gcf(), "figure.png")

    joblib.dump(model, model_file)
