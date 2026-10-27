import numpy as np
import pandas as pd

from src.helpers.helpers import calculate_distance


def add_distance_to_water(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Add all waterfront houses to the reference list.
    water_list = df.query("waterfront == 1")
    water_distance = []
    # For each row, calculate the distance to the nearest waterfront house.
    for idx in df.index:
        ref_list = []
        for x, y in zip(list(water_list["long"]), list(water_list["lat"])):
            ref_list.append(
                calculate_distance(df["long"][idx], df["lat"][idx], x, y).min()
            )
        water_distance.append(min(ref_list))

    # Create a new column from the previously computed list.
    df["water_distance"] = water_distance

    return df


def add_distance_from_center(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Absolute difference in latitude between the center and the property.
    df["delta_lat"] = np.absolute(47.62774 - df["lat"])
    # Absolute difference in longitude between the center and the property.
    df["delta_long"] = np.absolute(-122.24194 - df["long"])
    # Distance between the center and the property.
    df["center_distance"] = (
        ((df["delta_long"] * np.cos(np.radians(47.6219))) ** 2 + df["delta_lat"] ** 2)
        ** (1 / 2)
        * 2
        * np.pi
        * 6378
        / 360
    )

    return df


def add_sqft_price(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Create a variable for price per square foot of living space.
    df["sqft_price"] = (df.price / (df.sqft_living + df.sqft_lot)).round(2)

    return df


def data_processing(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = add_sqft_price(df)
    df = add_distance_from_center(df)
    df = add_distance_to_water(df)

    return df
