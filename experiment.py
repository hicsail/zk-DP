import time
import pandas as pd
from picozk import *
from picozk.poseidon_hash import PoseidonHash
from differential_privacy.add_noise import add_noise
from differential_privacy.preprocess import preprocess
from differential_privacy.prf import TripleDES_prf, Poseidon_prf, AES_prf
import matplotlib.pyplot as plt

SCALE = 1000
histogram = [0, 0, 0, 0, 0]


def update_hist(x):
    histogram[x] = histogram[x] + SCALE


def count(s):
    # Define the file path
    file_path = "irs/picozk_test.rel"

    # Initialize a variable to count lines
    line_count = 0

    # Open the file and read line by line
    with open(file_path, "r") as file:
        for line in file:
            line_count += 1

    million = 1000000
    line_count /= million

    # Print the total number of lines
    print(f"\nSize of input: {s}, Total number of lines in the file: {line_count} (* 10^6)")

    return line_count


if __name__ == "__main__":
    p = pow(2, 127) - 1
    # https://media.githubusercontent.com/media/usnistgov/SDNist/main/nist%20diverse%20communities%20data%20excerpts/massachusetts/ma2019.csv
    df = pd.read_csv("ma2019.csv")
    key = [1987034928369859712]
    keys = [1987034928369859712, 1987034925329849712, 15528198805165525]

    size = len(df)
    # interval = [0.1, 0.3, 0.5, 0.7, 1.0]
    interval = [0.1]
    sizes = [int(i * size) for i in interval]
    res_list = []

    preprocess(df)
    col = "PUMA"
    for s in sizes:
        # Pre-process
        _df = df[:s]
        _df[col].apply(update_hist)
        print("Init  Hist:", histogram)

        with PicoZKCompiler("irs/picozk_test", field=[p], options=["ram"]):  # TODO: Modify so that we can experiment both posiedon hash and 3DES
            poseidon_hash = PoseidonHash(p, alpha=17, input_rate=3)
            hashed_df = poseidon_hash.hash(list(_df[col]))

            sec_H = ZKList(histogram)

            # Triple DES
            start = time.time()
            prf_func = TripleDES_prf(keys, p)
            noisy_hist = add_noise(sec_H, p, prf_func)
            print("Noisy Hist:", noisy_hist)
            end = time.time()
            line_count = count(s)
            res_list.append([s, line_count, end - start, "tdes"])

            # Poseidon Hash
            start = time.time()
            prf_func = Poseidon_prf(keys, p)
            noisy_hist = add_noise(sec_H, p, prf_func)
            print("Noisy Hist:", noisy_hist)
            end = time.time()
            line_count = count(s)
            res_list.append([s, line_count, end - start, "poseidon"])

            # AES
            start = time.time()
            prf_func = AES_prf(key, p)
            noisy_hist = add_noise(sec_H, p, prf_func)
            print("Noisy Hist:", noisy_hist)
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
