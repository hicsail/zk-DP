import pandas as pd
from picozk import *
from picozk.poseidon_hash import PoseidonHash
from differential_privacy.add_noise import add_noise
from differential_privacy.preprocess import preprocess
from differential_privacy.prf import TripleDES_prf, Poseidon_prf, AES_prf
from differential_privacy.optimization import L2_optimization, calc_l2_gnorm

SCALE = 1000
histogram = [0, 0, 0, 0, 0]
child_histogram = [0, 0, 0]


def update_rootHist(x):
    histogram[x] = histogram[x] + SCALE


def update_childHist(x):
    child_histogram[x - 1] = child_histogram[x - 1] + SCALE


if __name__ == "__main__":
    p = pow(2, 127) - 1
    # https://media.githubusercontent.com/media/usnistgov/SDNist/main/nist%20diverse%20communities%20data%20excerpts/massachusetts/ma2019.csv
    df = pd.read_csv("ma2019.csv")

    key = [1987034928369859712]
    keys = [1987034928369859712, 1987034925329849712, 15528198805165525]

    # Pre-process
    preprocess(df)
    col = "PUMA"
    df[col].apply(update_rootHist)
    print("Init Hist:", histogram)

    with PicoZKCompiler("irs/picozk_test", field=[p], options=["ram"]):
        # Choice of PRF (Uncomment one line)
        prf_func = AES_prf(key, p)
        # prf_func = TripleDES_prf(keys, p)
        # prf_func = Poseidon_prf(keys, p)

        # Commit original data
        poseidon_hash = PoseidonHash(p, alpha=17, input_rate=3)
        hashed_df = poseidon_hash.hash(list(df[col]))

        # Noise Addition
        sec_H = ZKList(histogram)
        noisy_hist = add_noise(sec_H, p, prf_func)
        print("Noisy Hist:", noisy_hist)

        # Optimization done outside of ZK, but Proof is performed inside ZK
        l2_rate = 0.001
        l2_iter = 1000
        init_l2norm = calc_l2_gnorm(histogram, noisy_hist)
        opt_hist = L2_optimization(histogram, noisy_hist, l2_rate, l2_iter)
        print("Opt Hist  :", opt_hist)

        res_l2norm = calc_l2_gnorm(histogram, opt_hist)
        gnorm_check = mux((res_l2norm < init_l2norm), 0, 1)
        assert0(gnorm_check)
        assert val_of(gnorm_check) == 0

        ## Child Histogram

        c_col = "HOUSING_TYPE"
        print("\n Experimenting with child nodes querying ", c_col)

        for idx, _ in enumerate(opt_hist):
            df[c_col][df[col] == idx].apply(update_childHist)
            print("\nInit Child Hist:", child_histogram)

            # Noise Addition
            sec_child_H = ZKList(child_histogram)
            noisy_child_hist = add_noise(sec_child_H, p, prf_func)
            print("Noisy Child Hist:", noisy_child_hist)

            # Optimization done outside of ZK, but Proof is performed inside ZK
            l2_rate = 0.001
            l2_iter = 1000
            init_child_l2norm = calc_l2_gnorm(child_histogram, noisy_child_hist)
            opt_child_hist = L2_optimization(child_histogram, noisy_child_hist, l2_rate, l2_iter)
            print("Opt Child Hist  :", opt_child_hist)

            res_child_l2norm = calc_l2_gnorm(child_histogram, opt_child_hist)

            # ZK Proof
            gnorm_check = mux((res_child_l2norm < init_child_l2norm), 0, 1)
            assert0(gnorm_check)

            # Proof that the sum of the optimized child histograms stays within 5% of the optimized parent histogram
            assert sum(opt_child_hist) < 1.05 * opt_hist[idx] and sum(opt_child_hist) > 0.95 * opt_hist[idx]
            child_histogram = [0, 0, 0]
