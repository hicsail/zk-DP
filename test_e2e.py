import unittest
import pandas as pd
from picozk import *
from picozk.poseidon_hash import PoseidonHash
from differential_privacy.add_noise import add_noise
from differential_privacy.preprocess import preprocess
import pandas as pd

class TestPicoZKEndToEnd(unittest.TestCase):

    def test_e2e_process(self):
        
        p = pow(2, 61) - 1
        # https://media.githubusercontent.com/media/usnistgov/SDNist/main/nist%20diverse%20communities%20data%20excerpts/massachusetts/ma2019.csv
        df = pd.read_csv("ma2019.csv")

        with PicoZKCompiler("picozk_test", field=[p], options=["ram"]):
            key = 1987034928369859712  # TODO: Make a proper key

            for col in ['PUMA', 'NPF']:
                print("\nWorking on", col)

                # Replace negative values and N with ave.(excl. neg values)
                preprocess(df, col)

                # Commit data and key
                poseidon_hash = PoseidonHash(p, alpha=17, input_rate=3)
                hashed_df = poseidon_hash.hash(list(df[col]))
                _key = poseidon_hash.hash([key])

                # Add noise to df
                add_noise(df, col, p, hashed_df, key)


if __name__ == '__main__':
    unittest.main()
