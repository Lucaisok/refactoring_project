from pathlib import Path

import pandas as pd

from src.data_cleaning import clean_data
from src.data_loading import load_data
from src.data_processing import data_processing

OUTPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "processed.csv"


def run_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    cleaned_data = clean_data(df)
    processed_data = data_processing(cleaned_data)
    return processed_data


def main():
    df = run_pipeline(load_data())
    df.to_csv(OUTPUT_PATH, index=False)


if __name__ == "__main__":
    main()
