import unittest
import pandas as pd
from picozk import *
from picozk.poseidon_hash import PoseidonHash
from differential_privacy.add_noise import add_noise
from differential_privacy.preprocess import preprocess
from differential_privacy.laplase import gen_laplace_table
import pandas as pd


class TestPicoZKEndToEnd(unittest.TestCase):
    def test_e2e_process(self):
        p = pow(2, 127) - 1
        # https://media.githubusercontent.com/media/usnistgov/SDNist/main/nist%20diverse%20communities%20data%20excerpts/massachusetts/ma2019.csv
        df = pd.read_csv("ma2019.csv")
        cols = ["PUMA", "NPF"]

        key = 1987034928369859712  # TODO: Make a proper key

        with PicoZKCompiler("picozk_test", field=[p], options=["ram"]):
            # Replace negative values and N with ave.(excl. neg values)
            preprocess(df)

            # Secrefy Key
            key = SecretInt(key)

            # Create laplase table
            table = gen_laplace_table(sensitivity=1, p=p)
            zk_lap_table = ZKList(table)
            poseidon_hash = PoseidonHash(p, alpha=17, input_rate=3)
            _key = poseidon_hash.hash([key])

            for col in cols:
                print("\nWorking on", col)

                # Commit data and key
                poseidon_hash = PoseidonHash(p, alpha=17, input_rate=3)
                hashed_df = poseidon_hash.hash(list(df[col]))

                # Add noise to df
                add_noise(df, col, p, hashed_df, key, zk_lap_table)


if __name__ == "__main__":
    unittest.main()
