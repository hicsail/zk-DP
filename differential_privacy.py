import pandas as pd
from picozk import *
from picozk.poseidon_hash import PoseidonHash
from differential_privacy.add_noise import add_noise
from differential_privacy.preprocess import preprocess
from differential_privacy.prf import TripleDES_prf, Poseidon_prf, AES_prf
from differential_privacy.optimization import L2_optimization, calc_l2_gnorm

SCALE = 1000
histogram = [0, 0, 0, 0, 0]


def update_hist(x):
    histogram[x] = histogram[x] + SCALE


if __name__ == "__main__":
    p = pow(2, 127) - 1
    # https://media.githubusercontent.com/media/usnistgov/SDNist/main/nist%20diverse%20communities%20data%20excerpts/massachusetts/ma2019.csv
    df = pd.read_csv("ma2019.csv")

    key = [1987034928369859712]
    keys = [1987034928369859712, 1987034925329849712, 15528198805165525]

    # Pre-process
    preprocess(df)
    col = "PUMA"
    df[col].apply(update_hist)
    print("Init  Hist:", histogram)

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
