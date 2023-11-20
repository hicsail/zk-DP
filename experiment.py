from picozk import *
from picozk.poseidon_hash import PoseidonHash
import pandas as pd
import matplotlib.pyplot as plt
from differential_privacy.execute import execute
from experiment.counter import count
from differential_privacy.preprocess import preprocess
from differential_privacy.des_module.triple_des import triple_DES

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
        DES_inst = triple_DES(keys)
        # Replace negative values and N with ave.(excl. neg values)
        preprocess(df)

        for s in sizes:
            _df = df.iloc[:s].copy()
            execute(_df, p, DES_inst)
            line_count = count(s)
            res_list.append([s, line_count])

    res_df = pd.DataFrame(res_list, columns=["Size", "Counter"])

    # Plotting
    plt.figure(figsize=(10, 6))  # You can adjust the size of the figure
    plt.plot(res_df["Size"], res_df["Counter"], marker="o")  # marker='o' adds a circle marker to each data point
    plt.title("IR Growth")
    plt.xlabel("Size (s)")
    plt.ylabel("Line Count (in 10^6)")
    plt.grid(True)
    plt.show()
