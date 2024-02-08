import unittest
import pandas as pd
from picozk import *
from picozk.poseidon_hash import PoseidonHash
from differential_privacy.add_noise import add_noise
from differential_privacy.preprocess import preprocess
from differential_privacy.prf import TripleDES_prf, Poseidon_prf, AES_prf
from differential_privacy.optimization import L2_optimization, l2_obj_func


class TestPicoZKEndToEnd(unittest.TestCase):
    def test_e2e_process(self):
        SCALE = 1000

        histogram = [0, 0, 0, 0, 0]

        def update_hist(x):
            histogram[x] = histogram[x] + SCALE

        p = pow(2, 127) - 1
        # https://media.githubusercontent.com/media/usnistgov/SDNist/main/nist%20diverse%20communities%20data%20excerpts/massachusetts/ma2019.csv
        df = pd.read_csv("ma2019.csv")
        key = [1987034928369859712]
        keys = [1987034928369859712, 1987034925329849712, 15528198805165525]
        preprocess(df)
        col = "PUMA"
        df[col].apply(update_hist)

        with PicoZKCompiler("irs/picozk_test", field=[p], options=["ram"]):
            df = df[:10]
            poseidon_hash = PoseidonHash(p, alpha=17, input_rate=3)
            hashed_df = poseidon_hash.hash(list(df[col]))
            _key = poseidon_hash.hash(keys)

            # Implementation Body
            sec_H = ZKList(histogram)
            prf_func = TripleDES_prf(keys, p)
            noisy_hist = add_noise(sec_H, p, prf_func)

            prf_func = Poseidon_prf(keys, p)
            noisy_hist = add_noise(sec_H, p, prf_func)

            prf_func = AES_prf(key, p)
            noisy_hist = add_noise(sec_H, p, prf_func)

            # Optimization done outside of ZK, but proof inside ZK
            l2_rate = 0.001
            l2_iter = 1000
            init_norm = l2_obj_func(histogram, noisy_hist)
            opt_hist = L2_optimization(histogram, noisy_hist, l2_rate, l2_iter)
            res_norm = l2_obj_func(histogram, opt_hist)
            assert val_of(init_norm) > val_of(res_norm)


if __name__ == "__main__":
    unittest.main()
