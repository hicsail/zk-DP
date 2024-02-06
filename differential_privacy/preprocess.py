from picozk import *
import pandas as pd
import numpy as np


def preprocess(df):
    for col in df.columns:
        if col == "PUMA":
            mapping = {
                "25-00703": 0,
                "25-00503": 1,
                "25-01300": 2,
                "25-02800": 3,
                "25-01000": 4,
            }

            df[col] = df[col].replace(mapping)

        else:
            fillnas(df, col)

    col = "PUMA"
    sdf = df[col]

    return sdf


def fillnas(df, col):
    # Fill cells with value 'N' and negative values with the Global mean(excl. neg values)
    # Convert column to numeric, coercing errors to NaN
    numeric_col = pd.to_numeric(df[col], errors="coerce")

    # Calculate mean without 'N' and other non-numeric values
    positive_only = numeric_col[numeric_col > 0]
    mean_value = positive_only.mean()

    # Replace 'N' values and other non-numeric strings with the mean
    df[col] = df[col].replace("N", mean_value)

    # For any other non-numeric values that were coerced to NaN, fill with the mean
    df[col] = df[col].fillna(mean_value)

    # ParsingInt for the inequality check
    df[col] = df[col].astype(float).astype(int)

    # Replace negative values with the mean
    df[col] = np.where(df[col] < 0, mean_value, df[col])
