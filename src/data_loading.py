from pathlib import Path

import pandas as pd


def load_data():
    path = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "King_County_House_prices_dataset.csv"
    )
    data = pd.read_csv(path)
    return data


def main():
    load_data()


if __name__ == "__main__":
    main()
