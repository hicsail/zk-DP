from picozk import *


def preprocess(df):
    mapping = {
        "25-00703": 0,
        "25-00503": 1,
        "25-01300": 2,
        "25-02800": 3,
        "25-01000": 4,
    }

    sdf = df["PUMA"].replace(mapping).apply(SecretInt)
    return sdf
