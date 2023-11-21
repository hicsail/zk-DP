import unittest
import pandas as pd
from picozk import *
from picozk.poseidon_hash import PoseidonHash
from differential_privacy.execute import execute
from differential_privacy.preprocess import preprocess
from differential_privacy.des_module.triple_des import triple_DES


class TestPicoZKEndToEnd(unittest.TestCase):
    def test_e2e_process(self):
        p = pow(2, 127) - 1
        # https://media.githubusercontent.com/media/usnistgov/SDNist/main/nist%20diverse%20communities%20data%20excerpts/massachusetts/ma2019.csv
        df = pd.read_csv("ma2019.csv")
        cols = ["PUMA", "NPF"]
        keys = [1987034928369859712, 1987034925329849712, 15528198805165525]

        with PicoZKCompiler("picozk_test", field=[p], options=["ram"]):
            DES_inst = triple_DES(keys)

            # Replace negative values and N with ave.(excl. neg values)
            preprocess(df)

            poseidon_hash = PoseidonHash(p, alpha=17, input_rate=3)
            _key = poseidon_hash.hash(keys)

            # Implementation Body
            _df = df.iloc[:10].copy()
            execute(_df, p, DES_inst, cols)


if __name__ == "__main__":
    unittest.main()
