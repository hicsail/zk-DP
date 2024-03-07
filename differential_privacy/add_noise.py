from picozk import *
from .laplase import gen_laplace_table


def add_noise(sec_H, p, prf_func):
    """
    Time1: A prover commits a data and a key and generate a private key
    Time2: A beacon generates a random integer-string, x
    Time3: Seed = PRF(k, x)

    Proof:
        - Pub_data (Modified Sensus Data)
        - U = hash(seed)
        - noise = Lap-CDF[U]
        - for n in range(len(original)):
            assert0(data[n] + noise - Pub_data[n])
    """

    # Query the data
    laplace_table = gen_laplace_table(sensitivity=10, p=p)
    zk_lap_table = ZKList(laplace_table)
    noisy_hist = sec_H

    for i in range(len(sec_H)):
        print(i, end="\r")
        # look up laplace sample in the table
        x = prf_func.run(i)
        x = x.to_binary()
        shifted_x = x >> 114
        U = shifted_x.to_arithmetic()

        # Draw from lap distribution
        lap_draw = zk_lap_table[U]
        before = sec_H[i]
        noisy_hist[i] = sec_H[i] + lap_draw
        check = before + lap_draw - noisy_hist[i]
        assert0(check)

    return noisy_hist
