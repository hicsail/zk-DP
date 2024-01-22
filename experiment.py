import time
import pandas as pd
from picozk import *
from picozk.poseidon_hash import PoseidonHash
from differential_privacy.add_noise import add_noise
from differential_privacy.preprocess import preprocess
from differential_privacy.prf import TripleDES_prf, Poseidon_prf, Poseidon_prf_no_fieldswicth, AES_prf
import matplotlib.pyplot as plt
from experiment.counter import count

if __name__ == "__main__":
    p = pow(2, 127) - 1
    # https://media.githubusercontent.com/media/usnistgov/SDNist/main/nist%20diverse%20communities%20data%20excerpts/massachusetts/ma2019.csv
    df = pd.read_csv("ma2019.csv")
    keys = [1987034928369859712, 1987034925329849712, 15528198805165525]

    size = len(df)
    interval = [0.1, 0.3, 0.5, 0.7, 1.0]
    sizes = [int(i * size) for i in interval]
    res_list = []

    with PicoZKCompiler("irs/picozk_test", field=[p], options=["ram"]):  # TODO: Modify so that we can experiment both posiedon hash and 3DES
        # Replace negative values and N with ave.(excl. neg values)
        preprocess(df)

        for s in sizes:
            col = "PUMA"
            _df = df.iloc[:s].copy()
            sdf = _df[col]
            poseidon_hash = PoseidonHash(p, alpha=17, input_rate=3)
            hashed_df = poseidon_hash.hash(list(sdf))
            _key = poseidon_hash.hash(keys)

            # Triple DES
            start = time.time()
            prf_func = TripleDES_prf(keys, p)
            add_noise(sdf, p, hashed_df, prf_func)
            end = time.time()
            line_count = count(s)
            res_list.append([s, line_count, end - start, "tdes"])

            # Poseidon Hash
            start = time.time()
            prf_func = Poseidon_prf(keys, p)
            add_noise(sdf, p, hashed_df, prf_func)
            end = time.time()
            line_count = count(s)
            res_list.append([s, line_count, end - start, "poseidon"])

            # Poseidon Hash No field Switch
            start = time.time()
            prf_func = Poseidon_prf_no_fieldswicth(keys, p)
            add_noise(sdf, p, hashed_df, prf_func)
            end = time.time()
            line_count = count(s)
            res_list.append([s, line_count, end - start, "pos_no_fieldswicth"])

            # AES
            start = time.time()
            prf_func = AES_prf(keys, p)
            add_noise(sdf, p, hashed_df, prf_func)
            end = time.time()
            line_count = count(s)
            res_list.append([s, line_count, end - start, "aes"])

    res_df = pd.DataFrame(res_list, columns=["Size", "Counter", "Time", "PRF"])

    ## Measuring IR Growth

    # Filter and plot for Triple DES
    tdes_df = res_df[res_df["PRF"] == "tdes"]
    plt.plot(tdes_df["Size"], tdes_df["Counter"], marker="o", label="Triple DES")

    # Filter and plot for Poseidon
    poseidon_df = res_df[res_df["PRF"] == "poseidon"]
    plt.plot(poseidon_df["Size"], poseidon_df["Counter"], marker="o", label="Poseidon")

    # Filter and plot for Poseidon w/o field swicth
    poseidon_df = res_df[res_df["PRF"] == "pos_no_fieldswicth"]
    plt.plot(poseidon_df["Size"], poseidon_df["Counter"], marker="o", label="Poseidon(no field swicth)")

    # Filter and plot for AES
    poseidon_df = res_df[res_df["PRF"] == "aes"]
    plt.plot(poseidon_df["Size"], poseidon_df["Counter"], marker="o", label="AES")

    plt.title("IR Growth")
    plt.xlabel("Size (rows)")
    plt.ylabel("Lines in .rel (in 10^6)")
    plt.grid(True)
    plt.legend(loc="best")
    plt.show()

    ## Measuring Time

    # Filter and plot for Triple DES
    tdes_df = res_df[res_df["PRF"] == "tdes"]
    plt.plot(tdes_df["Size"], tdes_df["Time"], marker="o", label="Triple DES")

    # Filter and plot for Poseidon
    poseidon_df = res_df[res_df["PRF"] == "poseidon"]
    plt.plot(poseidon_df["Size"], poseidon_df["Time"], marker="o", label="Poseidon")

    # Filter and plot for Poseidon
    poseidon_df = res_df[res_df["PRF"] == "pos_no_fieldswicth"]
    plt.plot(poseidon_df["Size"], poseidon_df["Time"], marker="o", label="poseidon(no field swicth)")

    # Filter and plot for AES
    poseidon_df = res_df[res_df["PRF"] == "aes"]
    plt.plot(poseidon_df["Size"], poseidon_df["Time"], marker="o", label="AES")

    plt.title("RunTime")
    plt.xlabel("Size (rows)")
    plt.ylabel("Time")
    plt.grid(True)
    plt.legend(loc="best")
    plt.show()

    csv_file = "DP_analysis.csv"
    res_df.to_csv(csv_file, index=False)
