import pandas as pd

from data_loading import load_data


def remove_bedroom_outliers(df: pd.DataFrame) -> pd.DataFrame:
    print("before removing, size: ", df.shape)
    df["bath_bed_ratio"] = df["bathrooms"] / df["bedrooms"]
    invalid_ratio = (df["bath_bed_ratio"] >= 2) | (df["bath_bed_ratio"] <= 0.10)
    df = df.loc[~invalid_ratio].copy()
    df.drop(columns=["bath_bed_ratio"], inplace=True)
    print("after removing, size: ", df.shape)
    return df


def reconstruct_basement_size(df: pd.DataFrame) -> pd.DataFrame:
    print("reconstruct_basement_size run")
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
    print("missing values after filling", df.isna().sum())

    return df


def clean_data():
    data = load_data()
    df = data.copy()

    df = fill_missing_values(reconstruct_basement_size(remove_bedroom_outliers(df)))
    return df


def main():
    clean_data()


if __name__ == "__main__":
    main()
