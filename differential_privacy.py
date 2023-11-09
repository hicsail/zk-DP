from picozk import *
from differential_privacy import dp
from differential_privacy.preprocess import preprocess
import pandas as pd

if __name__ == "__main__":
    scale = 10
    # bitwidth is 13

    p = pow(2, 61) - 1
    # https://media.githubusercontent.com/media/usnistgov/SDNist/main/nist%20diverse%20communities%20data%20excerpts/massachusetts/ma2019.csv
    df = pd.read_csv("ma2019.csv")

    with PicoZKCompiler("irs/picozk_test", field=[p], options=["ram"]):
        sdf = preprocess(df)
        dp.run(sdf, p)
