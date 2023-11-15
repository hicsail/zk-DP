import pandas as pd
from picozk import *
from differential_privacy.execute import execute
from differential_privacy.preprocess import preprocess

if __name__ == "__main__":
    p = pow(2, 127) - 1
    # https://media.githubusercontent.com/media/usnistgov/SDNist/main/nist%20diverse%20communities%20data%20excerpts/massachusetts/ma2019.csv
    df = pd.read_csv("ma2019.csv")

    key = 1987034928369859712  # TODO: Make a proper key

    with PicoZKCompiler("irs/picozk_test", field=[p], options=["ram"]):
        # Replace negative values and N with ave.(excl. neg values)
        preprocess(df)
        execute(df, key, p)
