import unittest
import pandas as pd
from picozk import *
from picozk.poseidon_hash import PoseidonHash
from differential_privacy.add_noise import add_noise
from differential_privacy.preprocess import preprocess
from differential_privacy.prf import TripleDES_prf, Poseidon_prf, AES_prf
from differential_privacy.optimization import L2_optimization, calc_l2_gnorm


class TestPicoZKEndToEnd(unittest.TestCase):
    def test_e2e_process(self):
        SCALE = 1000
        histogram = [0, 0, 0, 0, 0]
        child_histogram = [0, 0, 0]

        def update_rootHist(x):
            histogram[x] = histogram[x] + SCALE

        def update_childHist(x):
            child_histogram[x - 1] = child_histogram[x - 1] + SCALE

        p = pow(2, 127) - 1
        # https://media.githubusercontent.com/media/usnistgov/SDNist/main/nist%20diverse%20communities%20data%20excerpts/massachusetts/ma2019.csv
        df = pd.read_csv("ma2019.csv")
        key = [1987034928369859712]
        keys = [1987034928369859712, 1987034925329849712, 15528198805165525]
        preprocess(df)
        col = "PUMA"
        df[col].apply(update_rootHist)

        with PicoZKCompiler("irs/picozk_test", field=[p], options=["ram"]):
            const_file = "const_data_dp.pkl"
            poseidon_hash = PoseidonHash(const_file, p, alpha=17, input_rate=3)
            hashed_df = poseidon_hash.hash(list(df[col].apply(SecretInt)))
            reveal(hashed_df)  # Assert hashed_df == pub hased df

            # Implementation Body
            sec_H = ZKList(histogram)
            prf_func = TripleDES_prf(keys, p)
            parent_hist = add_noise(sec_H, p, prf_func)

            prf_func = Poseidon_prf(keys, p)
            parent_hist = add_noise(sec_H, p, prf_func)

            prf_func = AES_prf(key, p)
            parent_hist = add_noise(sec_H, p, prf_func)

            ## Child Histogram

            c_col = "HOUSING_TYPE"
            print("\n Experimenting with child nodes querying ", c_col)

            res_parent = []

            for idx, _ in enumerate(parent_hist):
                df[c_col][df[col] == idx].apply(update_childHist)
                print("\nInit Child Hist:", child_histogram)

                # Noise Addition
                sec_child_H = ZKList(child_histogram)
                noisy_child_hist = add_noise(sec_child_H, p, prf_func)
                print("Noisy Child Hist:", noisy_child_hist)

                # Optimization done outside of ZK, but Proof is performed inside ZK
                l2_iter = 1500
                sec_opt_child_H = L2_optimization(parent_hist[idx], noisy_child_hist, l2_iter)
                print("Optimized Child Hist:", sec_opt_child_H)

                res_child_l2norm = calc_l2_gnorm(parent_hist[idx], sec_opt_child_H)

                # ZK Proof
                threshold = 10**6
                assert0(mux(res_child_l2norm < threshold, 0, 1))

                child_histogram = [0, 0, 0]
                res_parent.append(sum(sec_opt_child_H))

            print("Noisy Parent Hist:", parent_hist)
            print("Aggr. child hists", [val_of(elem) for elem in res_parent])
            for idx, sec_val in enumerate(res_parent):
                val = val_of(sec_val)
                assert val < 1.001 * val_of(parent_hist[idx]) and val > 0.999 * val_of(parent_hist[idx])


if __name__ == "__main__":
    unittest.main()
