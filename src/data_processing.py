import numpy as np
import pandas as pd

from src.helpers.helpers import calculate_distance


def add_distance_to_water(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Add all waterfront houses to the reference list.
    water_list = df.query("waterfront == 1")
    # Distance matrix: one row per house, one column per waterfront house.
    distances = calculate_distance(
        df["long"].to_numpy()[:, np.newaxis],
        df["lat"].to_numpy()[:, np.newaxis],
        water_list["long"].to_numpy()[np.newaxis, :],
        water_list["lat"].to_numpy()[np.newaxis, :],
    )
    # Keep the distance to the nearest waterfront house.
    df["water_distance"] = distances.min(axis=1)

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
