import unittest
import pandas as pd
from picozk import *
from differential_privacy.execute import execute
from differential_privacy.preprocess import preprocess


class TestPicoZKEndToEnd(unittest.TestCase):
    def test_e2e_process(self):
        p = pow(2, 127) - 1
        # https://media.githubusercontent.com/media/usnistgov/SDNist/main/nist%20diverse%20communities%20data%20excerpts/massachusetts/ma2019.csv
        df = pd.read_csv("ma2019.csv")
        cols = ["PUMA", "NPF"]
        key = 1987034928369859712  # TODO: Make a proper key
        key = [int(x) for x in bin(key)[2:]][:64] #TODO: Fix this
        if len(key) < 64:
            key = [0 for _ in range(64-len(key))] + key
        assert len(key) == 64

        with PicoZKCompiler("irs/picozk_test", field=[p], options=["ram"]):
            # Replace negative values and N with ave.(excl. neg values)
            preprocess(df)
            # Secrefy Key
            key = ZKList(key)
            execute(df, key, p, cols)


if __name__ == "__main__":
    unittest.main()
