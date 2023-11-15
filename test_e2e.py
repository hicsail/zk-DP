import unittest
from picozk import *
from differential_privacy.execute import execute
import pandas as pd


class TestPicoZKEndToEnd(unittest.TestCase):
    def test_e2e_process(self):
        p = pow(2, 127) - 1
        # https://media.githubusercontent.com/media/usnistgov/SDNist/main/nist%20diverse%20communities%20data%20excerpts/massachusetts/ma2019.csv
        df = pd.read_csv("ma2019.csv")
        cols = ["PUMA", "NPF"]

        key = 1987034928369859712  # TODO: Make a proper key

        with PicoZKCompiler("picozk_test", field=[p], options=["ram"]):
            execute(df, key, p, cols)


if __name__ == "__main__":
    unittest.main()
