from data_cleaning import clean_data


def data_processing():
    df = clean_data()
    print(df.head())


def main():
    data_processing()


if __name__ == "__main__":
    main()
