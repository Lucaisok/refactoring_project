import argparse
from pathlib import Path

import pandas as pd

from src.data_cleaning import clean_data
from src.data_loading import load_data
from src.data_processing import data_processing
from src.modeling import (
    MODEL_CONFIGS,
    ModelName,
    save_model,
    train_model,
)

CSV_OUTPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "processed.csv"


def run_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    cleaned_data = clean_data(df)
    processed_data = data_processing(cleaned_data)
    return processed_data


def main(selected_model: ModelName):
    df = run_pipeline(load_data())
    df.to_csv(CSV_OUTPUT_PATH, index=False)
    model = train_model(df, selected_model)
    path = MODEL_CONFIGS[selected_model].path
    save_model(model, path=path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=MODEL_CONFIGS, default="full")
    main(parser.parse_args().model)
