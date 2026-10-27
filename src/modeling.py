import os
from pathlib import Path

import pandas as pd
import skops.io as sio
from sklearn.compose import TransformedTargetRegressor
from sklearn.linear_model import ElasticNet
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

MODEL_PATH = Path(__file__).resolve().parents[1] / "model" / "model.bin"


def build_model() -> GridSearchCV:
    # Specify the hyperparameters to tune.
    # `alpha` controls the amount of regularization.
    param_grid = {
        "model__regressor__alpha": [0.01, 0.1, 1],
        "model__regressor__l1_ratio": [0.2, 0.5, 0.8],
    }

    # Keep preprocessing with the estimator for validation and inference.
    elastic_pipeline = Pipeline(
        [
            ("polynomial", PolynomialFeatures(2, include_bias=False)),
            ("scaler", StandardScaler()),
            (
                "model",
                TransformedTargetRegressor(
                    regressor=ElasticNet(max_iter=5000, tol=1e-4, precompute=True),
                    transformer=StandardScaler(),
                ),
            ),
        ]
    )

    # Pass the model to a parameter grid with 5-fold cross-validation.
    elastic_cv = GridSearchCV(
        elastic_pipeline,
        param_grid,
        cv=5,
        scoring="r2",
        verbose=2,
        n_jobs=1,
        error_score="raise",
    )

    return elastic_cv


def split_data(df: pd.DataFrame):
    # Remove columns that would cause data leakage or add no predictive value.
    drop_list = [
        "price",
        "sqft_price",
        "date",
        "delta_lat",
        "delta_long",
    ]
    features = [x for x in df.columns if x not in drop_list]

    X = df[features]
    y = df["price"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    return X_train, X_test, y_train, y_test


def prepare_features(df: pd.DataFrame):
    X_train, X_test, y_train, y_test = split_data(df)
    # Drop the `id` column; it identifies houses but has no predictive value.
    return X_train.drop(columns=["id"]), X_test.drop(columns=["id"]), y_train, y_test


def save_model(model, path: str | Path = MODEL_PATH):
    path = Path(path)
    # Create the directory if it does not already exist.
    os.makedirs(path.parent, exist_ok=True)

    with open(path, "wb") as f_out:
        sio.dump(model, f_out)


def train_model(df: pd.DataFrame):
    elastic_cv = build_model()
    X_train, X_test, y_train, y_test = prepare_features(df)
    # Train and optimize the model with grid search.
    elastic_cv.fit(X_train, y_train)

    elastic = elastic_cv.best_estimator_

    # Evaluate how well the model performs on the test data.
    print("Best params:", elastic_cv.best_params_)
    print("Test R^2:", round(elastic_cv.score(X_test, y_test), 3))

    return elastic
