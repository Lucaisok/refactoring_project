from pathlib import Path

import pandas as pd

DEFAULT_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "King_County_House_prices_dataset.csv"
)


def load_data(path: str | Path = DEFAULT_PATH):

    data = pd.read_csv(path)
    return data
