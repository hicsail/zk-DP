import unittest
import pandas as pd
from picozk import *
from picozk.poseidon_hash import PoseidonHash
from differential_privacy.execute import execute
from differential_privacy.preprocess import preprocess


class TestPicoZKEndToEnd(unittest.TestCase):
    def test_e2e_process(self):
        p = pow(2, 127) - 1
        # https://media.githubusercontent.com/media/usnistgov/SDNist/main/nist%20diverse%20communities%20data%20excerpts/massachusetts/ma2019.csv
        df = pd.read_csv("ma2019.csv")
        cols = ["PUMA", "NPF"]
        keys = [1987034928369859712, 1987034925329849712, 15528198805165525]  # TODO: Make a proper key
        for i in range(len(keys)):
            key = [int(x) for x in bin(keys[i])[2:]]
            if len(keys) > 64:
                keys[i] = key[:64]
            elif len(keys) < 64:
                keys[i] = [0 for _ in range(64 - len(key))] + key
            assert len(keys[i]) == 64

        with PicoZKCompiler("picozk_test", field=[p], options=["ram"]):
            # Replace negative values and N with ave.(excl. neg values)
            preprocess(df)

            poseidon_hash = PoseidonHash(p, alpha=17, input_rate=3)
            _key = poseidon_hash.hash(keys[0])
            _key = poseidon_hash.hash(keys[1])
            _key = poseidon_hash.hash(keys[2])

            # Secrefy Key
            keys = [ZKList(key) for key in keys]
            execute(df, keys, p, cols)


if __name__ == "__main__":
    unittest.main()
