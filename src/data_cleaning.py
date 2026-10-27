import pandas as pd


def remove_bedroom_outliers(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["bath_bed_ratio"] = df["bathrooms"] / df["bedrooms"]
    invalid_ratio = (df["bath_bed_ratio"] >= 2) | (df["bath_bed_ratio"] <= 0.10)
    df = df.loc[~invalid_ratio].copy()
    df.drop(columns=["bath_bed_ratio"], inplace=True)
    return df


def reconstruct_basement_size(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["sqft_basement"] = df["sqft_living"] - df["sqft_above"]
    return df


def fill_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["view"] = df["view"].fillna(0)
    df["waterfront"] = df["waterfront"].fillna(0)

    # If `yr_renovated` is 0 or missing, use the original build year instead.
    no_renovation = df["yr_renovated"].isna() | (df["yr_renovated"] == 0.0)
    df["last_known_change"] = (
        df["yr_built"].where(no_renovation, df["yr_renovated"]).astype(int)
    )
    # Drop the original `yr_renovated` and `yr_built` columns.
    df.drop("yr_renovated", axis=1, inplace=True)
    df.drop("yr_built", axis=1, inplace=True)

    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = remove_bedroom_outliers(df)
    df = reconstruct_basement_size(df)
    df = fill_missing_values(df)
    return df
