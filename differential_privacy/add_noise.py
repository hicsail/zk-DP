from picozk import *
from picozk.poseidon_hash import PoseidonHash
from .laplase import gen_laplace_table


def add_noise(sdf, p, hashed_df, prf_func):
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

    # Confirm the authenticity of the data
    poseidon_hash = PoseidonHash(p, alpha=17, input_rate=3)
    digest = poseidon_hash.hash(list(sdf))
    assert0(digest - hashed_df)

    # Query the data
    histogram = ZKList([0, 0, 0, 0, 0])  # TODO Parameterize size of hist

    def update_hist(x):
        histogram[x] = histogram[x] + 1000

    sdf.apply(update_hist)
    print(histogram)

    laplace_table = gen_laplace_table(sensitivity=1, p=p)
    zk_lap_table = ZKList(laplace_table)

    for i in range(len(histogram)):
        print(i, end="\r")
        # look up laplace sample in the table
        U = prf_func.run(i)

        # Draw from lap distribution
        lap_draw = zk_lap_table[U]
        before = histogram[i]
        histogram[i] = histogram[i] + lap_draw
        check = before + lap_draw - histogram[i]
        assert0(check)
        assert val_of(check) == 0

    print(histogram)
