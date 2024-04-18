import argparse
import os
import sys
import pandas as pd
import mlflow

parser = argparse.ArgumentParser(description="Data Validation")

parser.add_argument("--input", type=str, help="Clean Input folder", required=True)
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
mlflow_tracking_uri = args.mlflow_uri
experiment_name = args.mlflow_exp

if os.path.exists(input_file):
    print(f"Input file found: {input_file}")
    input_file = os.path.abspath(input_file)
else:
    print(f"Input file not found: {input_file}")
    sys.exit(1)

df = pd.read_csv(input_file)

mlflow.set_tracking_uri(mlflow_tracking_uri)
mlflow.set_experiment(experiment_name)

with mlflow.start_run(run_name="Data Validation") as run:
    mlflow.set_tag("release.version", "1.0.0")
    mlflow.log_param("Input file path", input_file)
    # data validation for numeric type

    for col in df.columns:
        if df[col].dtype == "float64" or df[col].dtype == "int64":
            pass
        else:
            print(
                "Data validation failed for column: ",
                col,
                " as it is not of numeric type",
            )
            mlflow.log_param("data_validation_status", "failed")
            mlflow.log_param("validation_failed_col", col)
            mlflow.log_param("validation_failed_reason", "non numeric column")
            sys.exit(1)

    # data validation check for missing values
    for col in df.columns:
        if df[col].isna().sum() > 0:
            print(
                "Data validation failed for column: ", col, " as it has missing values"
            )
            mlflow.log_param("data_validation_status", "failed")
            mlflow.log_param("validation_failed_col", col)
            mlflow.log_param("validation_failed_reason", "missing value in column")
            sys.exit(1)

    # data validation for rating should be between 0 and 10
    for col in df.columns:
        if "Rating" in col:
            if df[col].min() < 0 or df[col].max() > 10:
                print(
                    "Data validation failed for column: `",
                    col,
                    "` as rating is not between 0 and 10",
                )
                mlflow.log_param("data_validation_status", "failed")
                mlflow.log_param("validation_failed_col", col)
                mlflow.log_param("validation_failed_reason", "rating is out of range")
                sys.exit(1)

    for col in df.columns:
        mlflow.log_param(col + "_max", df[col].max())
        mlflow.log_param(col + "_min", df[col].max())
        mlflow.log_param(col + "_nunique", df[col].nunique())

    from evidently.test_suite import TestSuite
    from evidently.tests.base_test import generate_column_tests
    from evidently.tests import *

    tests = TestSuite(
        tests=[
            TestNumberOfColumnsWithMissingValues(),
            TestNumberOfRowsWithMissingValues(),
            TestNumberOfConstantColumns(),
            TestNumberOfDuplicatedRows(),
            TestNumberOfDuplicatedColumns(),
            TestColumnsType(),
        ]
    )

    tests.run(reference_data=None, current_data=df)
    tests_dict = tests.as_dict()
    mlflow.log_dict(tests_dict, "evidently_tests.json")

    if not tests_dict["summary"]["all_passed"]:
        mlflow.log_param("data_validation_status", "failed")
        mlflow.log_param("validation_failed_reason", "evidently tests failed")
        sys.exit(1)

    mlflow.log_param("data_validation_status", "success")
